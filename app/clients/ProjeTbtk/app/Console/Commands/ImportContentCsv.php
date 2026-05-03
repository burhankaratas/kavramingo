<?php

namespace App\Console\Commands;

use App\Models\FillBlankQuestion;
use App\Models\FlashcardQuestion;
use App\Models\MatchingPair;
use App\Models\McqQuestion;
use App\Models\Question;
use App\Models\Topic;
use App\Models\Unit;
use App\Support\UnitTopicResolver;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\DB;

class ImportContentCsv extends Command
{
    protected $signature = 'app:import-content-csv
        {type : unit|mcq|flashcard|matching|fill_blank}
        {file : CSV dosya yolu}';

    protected $description = 'Import content CSV with upsert semantics';

    public function handle(): int
    {
        $type = (string) $this->argument('type');
        $file = (string) $this->argument('file');

        if (!is_file($file) || !is_readable($file)) {
            $this->error('CSV dosyasi okunamiyor: ' . $file);
            return self::FAILURE;
        }

        $rows = $this->readCsv($file);
        if (count($rows) === 0) {
            $this->warn('CSV bos veya header disinda satir yok.');
            return self::SUCCESS;
        }

        return match ($type) {
            'unit' => $this->importUnit($rows),
            'mcq' => $this->importMcq($rows),
            'flashcard' => $this->importFlashcard($rows),
            'matching' => $this->importMatching($rows),
            'fill_blank' => $this->importFillBlank($rows),
            default => $this->unknownType($type),
        };
    }

    private function unknownType(string $type): int
    {
        $this->error('Gecersiz type: ' . $type);
        $this->line('Kullanilabilir: unit, mcq, flashcard, matching, fill_blank');
        return self::FAILURE;
    }

    /**
     * @return array<int, array<string, string>>
     */
    private function readCsv(string $file): array
    {
        $f = new \SplFileObject($file);
        $f->setFlags(\SplFileObject::READ_CSV | \SplFileObject::SKIP_EMPTY);

        $header = null;
        $rows = [];

        foreach ($f as $row) {
            if (!is_array($row)) {
                continue;
            }

            if ($row === [null] || count(array_filter($row, fn ($v) => trim((string) $v) !== '')) === 0) {
                continue;
            }

            if ($header === null) {
                $header = array_map(fn ($v) => trim((string) $v), $row);
                continue;
            }

            $assoc = [];
            foreach ($header as $i => $key) {
                if ($key === '') {
                    continue;
                }
                $assoc[$key] = trim((string) ($row[$i] ?? ''));
            }

            $rows[] = $assoc;
        }

        return $rows;
    }

    /**
     * @param array<string, string> $row
     */
    private function resolveTopic(array $row): ?Topic
    {
        $grade = (int) ($row['grade'] ?? 0);
        $unitNo = (int) ($row['unit_no'] ?? 0);
        $topicNo = (int) ($row['topic_no'] ?? 0);

        if (!in_array($grade, [9, 10, 11, 12], true) || $unitNo < 1 || $topicNo < 1) {
            return null;
        }

        $unit = Unit::query()->where('grade', $grade)->where('unit_no', $unitNo)->first();
        if (!$unit) {
            return null;
        }

        // topic_no gelmezse, unite icin default topic kullan
        if ($topicNo < 1) {
            return UnitTopicResolver::defaultTopicForUnitId($unit->id);
        }

        return Topic::query()->where('unit_id', $unit->id)->where('topic_no', $topicNo)->first();
    }

    private function importUnit(array $rows): int
    {
        $unitCreated = 0;
        $unitUpdated = 0;
        $skipped = 0;

        DB::beginTransaction();
        try {
            foreach ($rows as $row) {
                $grade = (int) ($row['grade'] ?? 0);
                $unitNo = (int) ($row['unit_no'] ?? 0);

                if (!in_array($grade, [9, 10, 11, 12], true) || $unitNo < 1) {
                    $skipped++;
                    continue;
                }

                $unit = Unit::withTrashed()->where('grade', $grade)->where('unit_no', $unitNo)->first();
                if ($unit) {
                    $unit->fill([
                        'name' => $row['unit_name'] ?? $unit->name,
                        'description' => $row['unit_description'] ?? $unit->description,
                        'order' => (int) ($row['unit_order'] ?? $unit->order ?? 0),
                    ]);
                    if ($unit->trashed()) {
                        $unit->restore();
                    }
                    $unit->save();
                    $unitUpdated++;
                } else {
                    $unit = Unit::create([
                        'grade' => $grade,
                        'unit_no' => $unitNo,
                        'name' => $row['unit_name'] ?? ('Unite ' . $unitNo),
                        'description' => $row['unit_description'] ?? null,
                        'order' => (int) ($row['unit_order'] ?? 0),
                    ]);
                    $unitCreated++;
                }

                UnitTopicResolver::defaultTopicForUnitId($unit->id);
            }

            DB::commit();
        } catch (\Throwable $e) {
            DB::rollBack();
            $this->error('Import hatasi: ' . $e->getMessage());
            return self::FAILURE;
        }

        $this->info("Unit created: $unitCreated, updated: $unitUpdated");
        $this->line("Skipped rows: $skipped");
        return self::SUCCESS;
    }

    private function importMcq(array $rows): int
    {
        $created = 0;
        $updated = 0;
        $skipped = 0;

        DB::beginTransaction();
        try {
            foreach ($rows as $row) {
                $questionCode = trim((string) ($row['question_code'] ?? ''));
                $topic = $this->resolveTopic($row);
                if ($questionCode === '' || !$topic) {
                    $skipped++;
                    continue;
                }

                $question = Question::withTrashed()->where('question_code', $questionCode)->first();
                $wasExisting = (bool) $question;
                if (!$question) {
                    $question = new Question();
                    $question->question_code = $questionCode;
                }

                $question->fill([
                    'topic_id' => $topic->id,
                    'quiz_type' => 'mcq',
                    'difficulty' => $row['difficulty'] ?: 'easy',
                    'prompt' => $row['prompt'] ?? null,
                    'order' => (int) ($row['order'] ?? 0),
                ]);
                if ($question->trashed()) {
                    $question->restore();
                }
                $question->save();

                $this->clearQuestionDetails($question);

                McqQuestion::updateOrCreate(
                    ['question_id' => $question->id],
                    [
                        'choice_a' => $row['choice_a'] ?? '',
                        'choice_b' => $row['choice_b'] ?? '',
                        'choice_c' => $row['choice_c'] ?? '',
                        'choice_d' => $row['choice_d'] ?? '',
                        'choice_e' => $row['choice_e'] ?? '',
                        'correct_choice' => strtoupper($row['correct_choice'] ?? 'A'),
                    ]
                );

                $wasExisting ? $updated++ : $created++;
            }

            DB::commit();
        } catch (\Throwable $e) {
            DB::rollBack();
            $this->error('Import hatasi: ' . $e->getMessage());
            return self::FAILURE;
        }

        $this->info("MCQ created: $created, updated: $updated, skipped: $skipped");
        return self::SUCCESS;
    }

    private function importFlashcard(array $rows): int
    {
        $created = 0;
        $updated = 0;
        $skipped = 0;

        DB::beginTransaction();
        try {
            foreach ($rows as $row) {
                $questionCode = trim((string) ($row['question_code'] ?? ''));
                $topic = $this->resolveTopic($row);
                if ($questionCode === '' || !$topic) {
                    $skipped++;
                    continue;
                }

                $question = Question::withTrashed()->where('question_code', $questionCode)->first();
                $wasExisting = (bool) $question;
                if (!$question) {
                    $question = new Question();
                    $question->question_code = $questionCode;
                }

                $question->fill([
                    'topic_id' => $topic->id,
                    'quiz_type' => 'flashcard',
                    'difficulty' => $row['difficulty'] ?: 'easy',
                    'prompt' => $row['prompt'] ?? null,
                    'order' => (int) ($row['order'] ?? 0),
                ]);
                if ($question->trashed()) {
                    $question->restore();
                }
                $question->save();

                $this->clearQuestionDetails($question);

                FlashcardQuestion::updateOrCreate(
                    ['question_id' => $question->id],
                    [
                        'front_text' => $row['front_text'] ?? '',
                        'back_text' => $row['back_text'] ?? '',
                    ]
                );

                $wasExisting ? $updated++ : $created++;
            }

            DB::commit();
        } catch (\Throwable $e) {
            DB::rollBack();
            $this->error('Import hatasi: ' . $e->getMessage());
            return self::FAILURE;
        }

        $this->info("Flashcard created: $created, updated: $updated, skipped: $skipped");
        return self::SUCCESS;
    }

    private function importFillBlank(array $rows): int
    {
        $created = 0;
        $updated = 0;
        $skipped = 0;

        DB::beginTransaction();
        try {
            foreach ($rows as $row) {
                $questionCode = trim((string) ($row['question_code'] ?? ''));
                $topic = $this->resolveTopic($row);
                if ($questionCode === '' || !$topic) {
                    $skipped++;
                    continue;
                }

                $question = Question::withTrashed()->where('question_code', $questionCode)->first();
                $wasExisting = (bool) $question;
                if (!$question) {
                    $question = new Question();
                    $question->question_code = $questionCode;
                }

                $question->fill([
                    'topic_id' => $topic->id,
                    'quiz_type' => 'fill_blank',
                    'difficulty' => $row['difficulty'] ?: 'easy',
                    'prompt' => $row['prompt'] ?? null,
                    'order' => (int) ($row['order'] ?? 0),
                ]);
                if ($question->trashed()) {
                    $question->restore();
                }
                $question->save();

                $this->clearQuestionDetails($question);

                FillBlankQuestion::updateOrCreate(
                    ['question_id' => $question->id],
                    [
                        'sentence_template' => $row['sentence_template'] ?? '',
                        'answer_text' => $row['answer_text'] ?? '',
                    ]
                );

                $wasExisting ? $updated++ : $created++;
            }

            DB::commit();
        } catch (\Throwable $e) {
            DB::rollBack();
            $this->error('Import hatasi: ' . $e->getMessage());
            return self::FAILURE;
        }

        $this->info("Fill blank created: $created, updated: $updated, skipped: $skipped");
        return self::SUCCESS;
    }

    private function importMatching(array $rows): int
    {
        $created = 0;
        $updated = 0;
        $skipped = 0;

        $grouped = [];
        foreach ($rows as $row) {
            $code = trim((string) ($row['question_code'] ?? ''));
            if ($code === '') {
                $skipped++;
                continue;
            }
            $grouped[$code][] = $row;
        }

        DB::beginTransaction();
        try {
            foreach ($grouped as $questionCode => $items) {
                $first = $items[0];
                $topic = $this->resolveTopic($first);
                if (!$topic) {
                    $skipped++;
                    continue;
                }

                $question = Question::withTrashed()->where('question_code', $questionCode)->first();
                $wasExisting = (bool) $question;
                if (!$question) {
                    $question = new Question();
                    $question->question_code = $questionCode;
                }

                $question->fill([
                    'topic_id' => $topic->id,
                    'quiz_type' => 'matching',
                    'difficulty' => $first['difficulty'] ?: 'easy',
                    'prompt' => $first['prompt'] ?? null,
                    'order' => (int) ($first['order'] ?? 0),
                ]);
                if ($question->trashed()) {
                    $question->restore();
                }
                $question->save();

                $this->clearQuestionDetails($question);

                $pairs = [];
                foreach ($items as $item) {
                    $left = trim((string) ($item['left_text'] ?? ''));
                    $right = trim((string) ($item['right_text'] ?? ''));
                    if ($left === '' || $right === '') {
                        continue;
                    }
                    $pairs[] = [
                        'left_text' => $left,
                        'right_text' => $right,
                        'order' => (int) ($item['pair_order'] ?? count($pairs)),
                    ];
                }

                if (count($pairs) < 3 || count($pairs) > 6) {
                    $skipped++;
                    continue;
                }

                MatchingPair::query()->where('question_id', $question->id)->delete();
                foreach ($pairs as $pair) {
                    MatchingPair::create([
                        'question_id' => $question->id,
                        'left_text' => $pair['left_text'],
                        'right_text' => $pair['right_text'],
                        'order' => $pair['order'],
                    ]);
                }

                $wasExisting ? $updated++ : $created++;
            }

            DB::commit();
        } catch (\Throwable $e) {
            DB::rollBack();
            $this->error('Import hatasi: ' . $e->getMessage());
            return self::FAILURE;
        }

        $this->info("Matching created: $created, updated: $updated, skipped: $skipped");
        return self::SUCCESS;
    }

    private function clearQuestionDetails(Question $question): void
    {
        McqQuestion::query()->where('question_id', $question->id)->delete();
        FlashcardQuestion::query()->where('question_id', $question->id)->delete();
        FillBlankQuestion::query()->where('question_id', $question->id)->delete();
        MatchingPair::query()->where('question_id', $question->id)->delete();
    }
}

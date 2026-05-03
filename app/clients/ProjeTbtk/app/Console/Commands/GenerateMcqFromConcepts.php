<?php

namespace App\Console\Commands;

use App\Models\Concept;
use App\Models\FillBlankQuestion;
use App\Models\FlashcardQuestion;
use App\Models\MatchingPair;
use App\Models\McqQuestion;
use App\Models\Question;
use App\Models\Unit;
use App\Support\UnitTopicResolver;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\DB;

class GenerateMcqFromConcepts extends Command
{
    protected $signature = 'app:generate-mcq-from-concepts
        {--grade= : Sadece belirli sinif (9,10,11,12)}
        {--per-unit=50 : Unite basi uretilecek MCQ sayisi}
        {--difficulty=easy : easy|medium|hard}';

    protected $description = 'Unite kavramlarindan 5 sikli MCQ sorulari uretir ve upsert eder';

    public function handle(): int
    {
        $perUnit = (int) $this->option('per-unit');
        if ($perUnit < 1) {
            $this->error('--per-unit en az 1 olmali.');
            return self::FAILURE;
        }

        $difficulty = (string) $this->option('difficulty');
        if (!in_array($difficulty, ['easy', 'medium', 'hard'], true)) {
            $this->error('--difficulty yalnizca easy, medium veya hard olabilir.');
            return self::FAILURE;
        }

        $unitsQuery = Unit::query()->orderBy('grade')->orderBy('unit_no');
        $gradeOpt = $this->option('grade');
        if ($gradeOpt !== null && $gradeOpt !== '') {
            $grade = (int) $gradeOpt;
            if (!in_array($grade, [9, 10, 11, 12], true)) {
                $this->error('--grade sadece 9, 10, 11 veya 12 olabilir.');
                return self::FAILURE;
            }
            $unitsQuery->where('grade', $grade);
        }

        $units = $unitsQuery->get();
        if ($units->isEmpty()) {
            $this->warn('Uygun unite bulunamadi.');
            return self::SUCCESS;
        }

        $summary = [
            'units_processed' => 0,
            'units_skipped' => 0,
            'questions_created' => 0,
            'questions_updated' => 0,
            'questions_deleted' => 0,
        ];

        foreach ($units as $unit) {
            $topic = UnitTopicResolver::defaultTopicForUnitId((int) $unit->id);
            if (!$topic) {
                $summary['units_skipped']++;
                continue;
            }

            $concepts = Concept::query()
                ->whereHas('topic', fn ($q) => $q->where('unit_id', $unit->id))
                ->whereNotNull('name')
                ->where('name', '<>', '')
                ->whereNotNull('definition')
                ->where('definition', '<>', '')
                ->orderBy('id')
                ->get(['id', 'name', 'definition']);

            if ($concepts->count() < 5) {
                $summary['units_skipped']++;
                $this->warn("[U{$unit->id}] en az 5 kavram olmadigi icin atlandi.");
                continue;
            }

            $summary['units_processed']++;
            $this->line("[U{$unit->id}] {$unit->grade}. sinif / {$unit->unit_no}. unite: {$perUnit} MCQ uretiliyor...");

            $targetCodes = [];

            DB::beginTransaction();
            try {
                for ($i = 1; $i <= $perUnit; $i++) {
                    $concept = $concepts[($i - 1) % $concepts->count()];
                    $code = "AUTO-MCQ-U{$unit->id}-Q" . str_pad((string) $i, 3, '0', STR_PAD_LEFT);
                    $targetCodes[] = $code;

                    $question = Question::withTrashed()->where('question_code', $code)->first();
                    $wasExisting = (bool) $question;

                    if (!$question) {
                        $question = new Question();
                        $question->question_code = $code;
                    }

                    $question->fill([
                        'topic_id' => $topic->id,
                        'quiz_type' => 'mcq',
                        'difficulty' => $difficulty,
                        'prompt' => $this->buildPrompt((string) $concept->definition, $i),
                        'order' => $i * 10,
                    ]);

                    if ($question->trashed()) {
                        $question->restore();
                    }

                    $question->save();
                    $this->clearQuestionDetails($question);

                    $optionPool = $this->buildOptions($concepts->all(), (int) $concept->id, $i);
                    $letters = ['A', 'B', 'C', 'D', 'E'];
                    $correctChoice = $letters[$optionPool['correct_index']];

                    McqQuestion::updateOrCreate(
                        ['question_id' => $question->id],
                        [
                            'choice_a' => $optionPool['options'][0],
                            'choice_b' => $optionPool['options'][1],
                            'choice_c' => $optionPool['options'][2],
                            'choice_d' => $optionPool['options'][3],
                            'choice_e' => $optionPool['options'][4],
                            'correct_choice' => $correctChoice,
                        ]
                    );

                    $wasExisting ? $summary['questions_updated']++ : $summary['questions_created']++;
                }

                $staleQuestions = Question::query()
                    ->where('quiz_type', 'mcq')
                    ->where('question_code', 'like', "AUTO-MCQ-U{$unit->id}-Q%")
                    ->whereNotIn('question_code', $targetCodes)
                    ->get();

                foreach ($staleQuestions as $stale) {
                    McqQuestion::query()->where('question_id', $stale->id)->delete();
                    $stale->delete();
                    $summary['questions_deleted']++;
                }

                DB::commit();
            } catch (\Throwable $e) {
                DB::rollBack();
                $this->error("[U{$unit->id}] hata: " . $e->getMessage());
                return self::FAILURE;
            }
        }

        $this->newLine();
        $this->info('Tamamlandi.');
        foreach ($summary as $key => $value) {
            $this->line($key . '=' . $value);
        }

        return self::SUCCESS;
    }

    private function buildPrompt(string $definition, int $index): string
    {
        $def = trim((string) preg_replace('/\s+/', ' ', $definition));
        $variant = (($index - 1) % 3) + 1;

        if ($variant === 1) {
            return "'{$def}' tanimi hangi kavrama aittir?";
        }

        if ($variant === 2) {
            return "Asagidaki tanima en uygun kavram hangisidir: {$def}";
        }

        return "Verilen tanima gore dogru kavrami seciniz: {$def}";
    }

    /**
     * @param array<int,\App\Models\Concept> $concepts
     * @return array{options: array<int,string>, correct_index: int}
     */
    private function buildOptions(array $concepts, int $correctConceptId, int $seed): array
    {
        $correct = null;
        $distractors = [];

        foreach ($concepts as $concept) {
            if ((int) $concept->id === $correctConceptId) {
                $correct = (string) $concept->name;
                continue;
            }
            $distractors[] = (string) $concept->name;
        }

        if ($correct === null) {
            $correct = '';
        }

        $count = count($distractors);
        $picked = [];
        for ($k = 0; $k < 4; $k++) {
            $idx = ($seed + ($k * 3)) % $count;
            while (in_array($distractors[$idx], $picked, true)) {
                $idx = ($idx + 1) % $count;
            }
            $picked[] = $distractors[$idx];
        }

        $options = [$picked[0], $picked[1], $picked[2], $picked[3], $correct];
        $correctIndex = ($seed - 1) % 5;

        if ($correctIndex !== 4) {
            $tmp = $options[$correctIndex];
            $options[$correctIndex] = $options[4];
            $options[4] = $tmp;
        }

        return [
            'options' => $options,
            'correct_index' => $correctIndex,
        ];
    }

    private function clearQuestionDetails(Question $question): void
    {
        McqQuestion::query()->where('question_id', $question->id)->delete();
        FlashcardQuestion::query()->where('question_id', $question->id)->delete();
        FillBlankQuestion::query()->where('question_id', $question->id)->delete();
        MatchingPair::query()->where('question_id', $question->id)->delete();
    }
}

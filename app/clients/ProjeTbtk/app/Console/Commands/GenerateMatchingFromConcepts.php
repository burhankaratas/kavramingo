<?php

namespace App\Console\Commands;

use App\Models\Concept;
use App\Models\MatchingPair;
use App\Models\Question;
use App\Models\Unit;
use App\Support\UnitTopicResolver;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\DB;

class GenerateMatchingFromConcepts extends Command
{
    protected $signature = 'app:generate-matching-from-concepts
        {--grade= : Sadece belirli sinif (9,10,11,12)}
        {--pair-count=4 : Bir sorudaki eslestirme cift sayisi (3-6)}
        {--max-per-unit=0 : Unite basi maksimum soru sayisi (0 = limitsiz)}';

    protected $description = 'Unite kavramlarindan otomatik eslestirme sorulari uretir ve upsert eder';

    public function handle(): int
    {
        $pairCount = (int) $this->option('pair-count');
        if ($pairCount < 3 || $pairCount > 6) {
            $this->error('--pair-count 3 ile 6 arasinda olmali.');
            return self::FAILURE;
        }

        $maxPerUnit = (int) $this->option('max-per-unit');
        $gradeOpt = $this->option('grade');

        $unitsQuery = Unit::query()->orderBy('grade')->orderBy('unit_no');
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
            'questions_created' => 0,
            'questions_updated' => 0,
            'pairs_written' => 0,
            'units_skipped' => 0,
        ];

        foreach ($units as $unit) {
            $topic = UnitTopicResolver::defaultTopicForUnitId((int) $unit->id);
            if (!$topic) {
                $summary['units_skipped']++;
                continue;
            }

            $concepts = Concept::query()
                ->whereHas('topic', fn ($q) => $q->where('unit_id', $unit->id))
                ->whereNotNull('definition')
                ->where('definition', '<>', '')
                ->orderBy('id')
                ->get(['id', 'name', 'definition']);

            if ($concepts->count() < $pairCount) {
                $summary['units_skipped']++;
                continue;
            }

            $summary['units_processed']++;
            $this->line("[U{$unit->id}] {$unit->grade}. sinif / {$unit->unit_no}. unite: kombinasyon uretiliyor...");

            $combinations = $this->conceptIdCombinations($concepts->pluck('id')->all(), $pairCount);
            $writtenForUnit = 0;

            DB::beginTransaction();
            try {
                foreach ($combinations as $comboIds) {
                    if ($maxPerUnit > 0 && $writtenForUnit >= $maxPerUnit) {
                        break;
                    }

                    $code = $this->makeQuestionCode((int) $unit->id, $pairCount, $comboIds);
                    $question = Question::withTrashed()->where('question_code', $code)->first();
                    $wasExisting = (bool) $question;

                    if (!$question) {
                        $question = new Question();
                        $question->question_code = $code;
                    }

                    $question->fill([
                        'topic_id' => $topic->id,
                        'quiz_type' => 'matching',
                        'difficulty' => 'medium',
                        'prompt' => 'Kavramlari tanimlariyla eslestiriniz.',
                        'order' => ($writtenForUnit + 1) * 10,
                    ]);

                    if ($question->trashed()) {
                        $question->restore();
                    }

                    $question->save();

                    MatchingPair::query()->where('question_id', $question->id)->delete();

                    $pairs = [];
                    foreach ($comboIds as $idx => $conceptId) {
                        $concept = $concepts->firstWhere('id', $conceptId);
                        if (!$concept) {
                            continue;
                        }
                        $pairs[] = [
                            'question_id' => $question->id,
                            'left_text' => $concept->name,
                            'right_text' => $concept->definition,
                            'order' => ($idx + 1) * 10,
                            'created_at' => now(),
                            'updated_at' => now(),
                        ];
                    }

                    if (count($pairs) >= 3) {
                        MatchingPair::insert($pairs);
                        $summary['pairs_written'] += count($pairs);
                        $writtenForUnit++;
                        if ($wasExisting) {
                            $summary['questions_updated']++;
                        } else {
                            $summary['questions_created']++;
                        }
                    }
                }

                DB::commit();
            } catch (\Throwable $e) {
                DB::rollBack();
                $this->error("[U{$unit->id}] hata: " . $e->getMessage());
                return self::FAILURE;
            }

            $this->line("  -> yazilan soru: {$writtenForUnit}");
        }

        $this->newLine();
        $this->info('Tamamlandi.');
        foreach ($summary as $k => $v) {
            $this->line($k . '=' . $v);
        }

        return self::SUCCESS;
    }

    /**
     * @param array<int,int> $ids
     * @return array<int,array<int,int>>
     */
    private function conceptIdCombinations(array $ids, int $pick): array
    {
        $result = [];
        $n = count($ids);

        $recurse = function (int $start, array $current) use (&$recurse, &$result, $ids, $n, $pick): void {
            if (count($current) === $pick) {
                $result[] = $current;
                return;
            }

            for ($i = $start; $i < $n; $i++) {
                $next = $current;
                $next[] = $ids[$i];
                $recurse($i + 1, $next);
            }
        };

        $recurse(0, []);
        return $result;
    }

    /**
     * @param array<int,int> $conceptIds
     */
    private function makeQuestionCode(int $unitId, int $pairCount, array $conceptIds): string
    {
        sort($conceptIds);
        $hash = substr(sha1(implode('-', $conceptIds)), 0, 12);
        return "AUTO-MAT-U{$unitId}-P{$pairCount}-{$hash}";
    }
}

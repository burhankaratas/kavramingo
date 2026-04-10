<?php

namespace App\Console\Commands;

use App\Models\Concept;
use App\Models\FillBlankQuestion;
use App\Models\Question;
use App\Models\Unit;
use App\Support\UnitTopicResolver;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\DB;

class GenerateFillBlankFromConcepts extends Command
{
    protected $signature = 'app:generate-fillblank-from-concepts
        {--grade= : Sadece belirli sinif (9,10,11,12)}
        {--max-per-unit=0 : Unite basi maksimum soru (0 = limitsiz)}
        {--variants=2 : Kavram basi kac farkli soru turetilecek (1-2)}';

    protected $description = 'Unite kavramlarindan otomatik bosluk doldurma sorulari uretir ve upsert eder';

    public function handle(): int
    {
        $maxPerUnit = (int) $this->option('max-per-unit');
        $variants = (int) $this->option('variants');
        if (!in_array($variants, [1, 2], true)) {
            $this->error('--variants yalnizca 1 veya 2 olabilir.');
            return self::FAILURE;
        }

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

            if ($concepts->isEmpty()) {
                $summary['units_skipped']++;
                continue;
            }

            $summary['units_processed']++;
            $this->line("[U{$unit->id}] {$unit->grade}. sinif / {$unit->unit_no}. unite: bosluk doldurma uretiliyor...");

            $writtenForUnit = 0;

            DB::beginTransaction();
            try {
                foreach ($concepts as $concept) {
                    if ($maxPerUnit > 0 && $writtenForUnit >= $maxPerUnit) {
                        break;
                    }

                    $templates = $this->buildTemplates((string) $concept->definition, $variants);
                    foreach ($templates as $idx => $sentenceTemplate) {
                        if ($maxPerUnit > 0 && $writtenForUnit >= $maxPerUnit) {
                            break;
                        }

                        $code = "AUTO-FB-U{$unit->id}-C{$concept->id}-V" . ($idx + 1);
                        $question = Question::withTrashed()->where('question_code', $code)->first();
                        $wasExisting = (bool) $question;

                        if (!$question) {
                            $question = new Question();
                            $question->question_code = $code;
                        }

                        $question->fill([
                            'topic_id' => $topic->id,
                            'quiz_type' => 'fill_blank',
                            'difficulty' => 'easy',
                            'prompt' => 'Asagidaki tanima uygun kavrami yaziniz.',
                            'order' => ($writtenForUnit + 1) * 10,
                        ]);

                        if ($question->trashed()) {
                            $question->restore();
                        }

                        $question->save();

                        FillBlankQuestion::updateOrCreate(
                            ['question_id' => $question->id],
                            [
                                'sentence_template' => $sentenceTemplate,
                                'answer_text' => (string) $concept->name,
                            ]
                        );

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
     * @return array<int,string>
     */
    private function buildTemplates(string $definition, int $variants): array
    {
        $def = trim(preg_replace('/\s+/', ' ', $definition) ?? $definition);

        $templates = [
            $def . ' Bu kavrama ___ denir.',
        ];

        if ($variants >= 2) {
            $templates[] = 'Tanim: ' . $def . ' Yukaridaki tanimin kavrami: ___';
        }

        return $templates;
    }
}

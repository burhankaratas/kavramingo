<?php

namespace App\Http\Controllers\Api\V1;

use App\Http\Controllers\Controller;
use App\Models\Concept;
use App\Models\Question;
use App\Models\Topic;
use App\Models\Unit;
use App\Support\ApiResponse;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class QuestionFeedController extends Controller
{
    use ApiResponse;

    public function quizFeed(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'grade' => ['required', 'integer', 'in:9,10,11,12'],
            'unit_id' => ['required', 'integer', 'exists:units,id'],
            'quiz_type' => ['required', 'in:mcq,flashcard,matching,fill_blank'],
        ]);

        $unit = Unit::query()->whereKey($validated['unit_id'])->where('grade', $validated['grade'])->first();
        if (!$unit) {
            return $this->error('UNIT_NOT_FOUND', 'Uygun unite bulunamadi.', [], 404);
        }

        $configuredCount = $unit->quizConfigs()
            ->where('quiz_type', $validated['quiz_type'])
            ->value('question_count') ?? 5;

        $questions = Question::query()
            ->where('quiz_type', $validated['quiz_type'])
            ->whereHas('topic', fn ($q) => $q->where('unit_id', $unit->id))
            ->inRandomOrder()
            ->limit((int) $configuredCount)
            ->get();

        $mappedQuestions = $this->mapQuestions($questions);

        if ($validated['quiz_type'] === 'flashcard' && count($mappedQuestions) < (int) $configuredCount) {
            $needed = (int) $configuredCount - count($mappedQuestions);
            $mappedQuestions = array_merge(
                $mappedQuestions,
                $this->conceptFlashcardsForUnit($unit, $needed, $mappedQuestions)
            );
        }

        return $this->ok([
            'unit' => [
                'id' => $unit->id,
                'grade' => $unit->grade,
                'unit_no' => $unit->unit_no,
                'name' => $unit->name,
            ],
            'quiz_type' => $validated['quiz_type'],
            'question_count' => (int) $configuredCount,
            'questions' => $mappedQuestions,
        ]);
    }

    public function placementFeed(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'grade' => ['required', 'integer', 'in:9,10,11,12'],
        ]);

        $grade = (int) $validated['grade'];

        $units = Unit::query()
            ->where('grade', '<=', $grade)
            ->orderBy('grade')
            ->orderBy('unit_no')
            ->get();

        $payload = [];
        foreach ($units as $unit) {
            $question = Question::query()
                ->where('quiz_type', 'mcq')
                ->whereHas('topic', fn ($q) => $q->where('unit_id', $unit->id))
                ->inRandomOrder()
                ->first();

            if (!$question) {
                continue;
            }

            $mapped = $this->mapQuestions(collect([$question]));
            if (count($mapped) === 0) {
                continue;
            }

            $payload[] = [
                'unit' => [
                    'id' => $unit->id,
                    'grade' => $unit->grade,
                    'unit_no' => $unit->unit_no,
                    'name' => $unit->name,
                ],
                'question' => $mapped[0],
            ];
        }

        return $this->ok([
            'grade' => $grade,
            'threshold_completed' => 70,
            'items' => $payload,
        ]);
    }

    private function mapQuestions($questions): array
    {
        foreach ($questions as $question) {
            if ($question instanceof Question) {
                $question->load(['topic', 'mcq', 'flashcard', 'fillBlank', 'matchingPairs']);
            }
        }

        return collect($questions)->map(function (Question $question) {
            $base = [
                'id' => $question->id,
                'question_code' => $question->question_code,
                'quiz_type' => $question->quiz_type,
                'difficulty' => $question->difficulty,
                'prompt' => $question->prompt,
                'topic_id' => $question->topic_id,
                'topic_name' => $question->topic?->name,
            ];

            if ($question->quiz_type === 'mcq' && $question->mcq) {
                $base['choices'] = [
                    'A' => $question->mcq->choice_a,
                    'B' => $question->mcq->choice_b,
                    'C' => $question->mcq->choice_c,
                    'D' => $question->mcq->choice_d,
                    'E' => $question->mcq->choice_e,
                ];
                $base['correct_choice'] = $question->mcq->correct_choice;
            }

            if ($question->quiz_type === 'flashcard' && $question->flashcard) {
                $base['front_text'] = $question->flashcard->front_text;
                $base['back_text'] = $question->flashcard->back_text;
            }

            if ($question->quiz_type === 'fill_blank' && $question->fillBlank) {
                $base['sentence_template'] = $question->fillBlank->sentence_template;
                $base['answer_text'] = $question->fillBlank->answer_text;
                $base['similarity_threshold'] = 85;
            }

            if ($question->quiz_type === 'matching') {
                $base['pairs'] = $question->matchingPairs->map(fn ($pair) => [
                    'left_text' => $pair->left_text,
                    'right_text' => $pair->right_text,
                ])->values();
            }

            return $base;
        })->values()->all();
    }

    private function conceptFlashcardsForUnit(Unit $unit, int $limit, array $existingMapped): array
    {
        if ($limit <= 0) {
            return [];
        }

        $existingCodes = [];
        foreach ($existingMapped as $item) {
            $code = (string) ($item['question_code'] ?? '');
            if ($code !== '') {
                $existingCodes[$code] = true;
            }
        }

        $concepts = Concept::query()
            ->whereHas('topic', fn ($q) => $q->where('unit_id', $unit->id))
            ->whereNotNull('definition')
            ->where('definition', '<>', '')
            ->inRandomOrder()
            ->limit($limit * 3)
            ->get();

        $cards = [];
        foreach ($concepts as $concept) {
            $code = 'concept_' . $concept->id;
            if (isset($existingCodes[$code])) {
                continue;
            }

            $cards[] = [
                'id' => (int) $concept->id,
                'question_code' => $code,
                'quiz_type' => 'flashcard',
                'difficulty' => 'easy',
                'prompt' => null,
                'topic_id' => $concept->topic_id,
                'topic_name' => $concept->topic?->name,
                'front_text' => $concept->name,
                'back_text' => $concept->definition,
            ];

            if (count($cards) >= $limit) {
                break;
            }
        }

        return $cards;
    }
}

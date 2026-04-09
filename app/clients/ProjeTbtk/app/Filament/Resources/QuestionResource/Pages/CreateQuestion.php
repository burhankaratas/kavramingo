<?php

namespace App\Filament\Resources\QuestionResource\Pages;

use App\Filament\Resources\QuestionResource;
use App\Models\Question;
use Filament\Actions;
use Filament\Resources\Pages\CreateRecord;

class CreateQuestion extends CreateRecord
{
    protected static string $resource = QuestionResource::class;

    protected function handleRecordCreation(array $data): Question
    {
        $data = QuestionResource::mutateDataToTopic($data);

        $mcq = $data['mcq'] ?? null;
        $flashcard = $data['flashcard'] ?? null;
        $fillBlank = $data['fill_blank'] ?? null;
        $matchingPairs = $data['matching_pairs'] ?? [];

        unset($data['mcq'], $data['flashcard'], $data['fill_blank'], $data['matching_pairs']);

        /** @var Question $question */
        $question = static::getModel()::create($data);

        if ($question->quiz_type === 'mcq' && is_array($mcq)) {
            $question->mcq()->create($mcq);
        }

        if ($question->quiz_type === 'flashcard' && is_array($flashcard)) {
            $question->flashcard()->create($flashcard);
        }

        if ($question->quiz_type === 'fill_blank' && is_array($fillBlank)) {
            $question->fillBlank()->create($fillBlank);
        }

        if ($question->quiz_type === 'matching' && is_array($matchingPairs)) {
            foreach (array_values($matchingPairs) as $idx => $pair) {
                $question->matchingPairs()->create([
                    'left_text' => (string) ($pair['left_text'] ?? ''),
                    'right_text' => (string) ($pair['right_text'] ?? ''),
                    'order' => (int) ($pair['order'] ?? $idx),
                ]);
            }
        }

        return $question;
    }
}

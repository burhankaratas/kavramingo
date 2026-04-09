<?php

namespace App\Filament\Resources\QuestionResource\Pages;

use App\Filament\Resources\QuestionResource;
use App\Models\Question;
use Filament\Actions;
use Filament\Resources\Pages\EditRecord;

class EditQuestion extends EditRecord
{
    protected static string $resource = QuestionResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\ViewAction::make(),
            Actions\DeleteAction::make(),
            Actions\ForceDeleteAction::make(),
            Actions\RestoreAction::make(),
        ];
    }

    protected function mutateFormDataBeforeFill(array $data): array
    {
        /** @var Question $record */
        $record = $this->record;
        $record->load(['mcq', 'flashcard', 'fillBlank', 'matchingPairs']);

        $data['mcq'] = $record->mcq?->only(['choice_a', 'choice_b', 'choice_c', 'choice_d', 'correct_choice']);
        $data['flashcard'] = $record->flashcard?->only(['front_text', 'back_text']);
        $data['fill_blank'] = $record->fillBlank?->only(['sentence_template', 'answer_text']);
        $data['matching_pairs'] = $record->matchingPairs->map(fn ($pair) => [
            'left_text' => $pair->left_text,
            'right_text' => $pair->right_text,
            'order' => $pair->order,
        ])->all();

        return $data;
    }

    protected function handleRecordUpdate($record, array $data): Question
    {
        /** @var Question $record */
        $mcq = $data['mcq'] ?? null;
        $flashcard = $data['flashcard'] ?? null;
        $fillBlank = $data['fill_blank'] ?? null;
        $matchingPairs = $data['matching_pairs'] ?? [];

        unset($data['mcq'], $data['flashcard'], $data['fill_blank'], $data['matching_pairs']);

        $record->update($data);

        $record->mcq()?->delete();
        $record->flashcard()?->delete();
        $record->fillBlank()?->delete();
        $record->matchingPairs()->delete();

        if ($record->quiz_type === 'mcq' && is_array($mcq)) {
            $record->mcq()->create($mcq);
        }

        if ($record->quiz_type === 'flashcard' && is_array($flashcard)) {
            $record->flashcard()->create($flashcard);
        }

        if ($record->quiz_type === 'fill_blank' && is_array($fillBlank)) {
            $record->fillBlank()->create($fillBlank);
        }

        if ($record->quiz_type === 'matching' && is_array($matchingPairs)) {
            foreach (array_values($matchingPairs) as $idx => $pair) {
                $record->matchingPairs()->create([
                    'left_text' => (string) ($pair['left_text'] ?? ''),
                    'right_text' => (string) ($pair['right_text'] ?? ''),
                    'order' => (int) ($pair['order'] ?? $idx),
                ]);
            }
        }

        return $record;
    }
}

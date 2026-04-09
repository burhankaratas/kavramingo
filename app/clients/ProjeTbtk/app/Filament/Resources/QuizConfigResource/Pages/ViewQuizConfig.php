<?php

namespace App\Filament\Resources\QuizConfigResource\Pages;

use App\Filament\Resources\QuizConfigResource;
use Filament\Actions;
use Filament\Resources\Pages\ViewRecord;

class ViewQuizConfig extends ViewRecord
{
    protected static string $resource = QuizConfigResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\EditAction::make(),
        ];
    }
}

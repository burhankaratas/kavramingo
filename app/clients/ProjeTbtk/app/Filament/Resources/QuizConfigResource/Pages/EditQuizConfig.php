<?php

namespace App\Filament\Resources\QuizConfigResource\Pages;

use App\Filament\Resources\QuizConfigResource;
use Filament\Actions;
use Filament\Resources\Pages\EditRecord;

class EditQuizConfig extends EditRecord
{
    protected static string $resource = QuizConfigResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\ViewAction::make(),
            Actions\DeleteAction::make(),
        ];
    }
}

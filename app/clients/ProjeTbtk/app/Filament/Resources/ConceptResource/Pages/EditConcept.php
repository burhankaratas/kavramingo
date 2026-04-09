<?php

namespace App\Filament\Resources\ConceptResource\Pages;

use App\Filament\Resources\ConceptResource;
use Filament\Actions;
use Filament\Resources\Pages\EditRecord;

class EditConcept extends EditRecord
{
    protected static string $resource = ConceptResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\ViewAction::make(),
            Actions\DeleteAction::make(),
            Actions\ForceDeleteAction::make(),
            Actions\RestoreAction::make(),
        ];
    }
}

<?php

namespace App\Filament\Resources\PlacementRuleResource\Pages;

use App\Filament\Resources\PlacementRuleResource;
use Filament\Actions;
use Filament\Resources\Pages\EditRecord;

class EditPlacementRule extends EditRecord
{
    protected static string $resource = PlacementRuleResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\ViewAction::make(),
            Actions\DeleteAction::make(),
        ];
    }
}

<?php

namespace App\Filament\Resources\PlacementRuleResource\Pages;

use App\Filament\Resources\PlacementRuleResource;
use Filament\Actions;
use Filament\Resources\Pages\ViewRecord;

class ViewPlacementRule extends ViewRecord
{
    protected static string $resource = PlacementRuleResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\EditAction::make(),
        ];
    }
}

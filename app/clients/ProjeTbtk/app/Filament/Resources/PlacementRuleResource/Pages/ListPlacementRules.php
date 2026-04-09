<?php

namespace App\Filament\Resources\PlacementRuleResource\Pages;

use App\Filament\Resources\PlacementRuleResource;
use Filament\Actions;
use Filament\Resources\Pages\ListRecords;

class ListPlacementRules extends ListRecords
{
    protected static string $resource = PlacementRuleResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\CreateAction::make(),
        ];
    }
}

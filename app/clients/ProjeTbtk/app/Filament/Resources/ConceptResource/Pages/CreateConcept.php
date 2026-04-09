<?php

namespace App\Filament\Resources\ConceptResource\Pages;

use App\Filament\Resources\ConceptResource;
use App\Models\Concept;
use Filament\Actions;
use Filament\Resources\Pages\CreateRecord;

class CreateConcept extends CreateRecord
{
    protected static string $resource = ConceptResource::class;

    protected function handleRecordCreation(array $data): Concept
    {
        $data = ConceptResource::mutateDataToTopic($data);

        /** @var Concept $concept */
        $concept = static::getModel()::create($data);
        return $concept;
    }
}

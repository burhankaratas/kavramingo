<?php

namespace App\Filament\Resources\UnitResource\Pages;

use App\Filament\Resources\UnitResource;
use App\Filament\Support\HandlesIntegrityError;
use Filament\Actions;
use Filament\Resources\Pages\CreateRecord;

class CreateUnit extends CreateRecord
{
    use HandlesIntegrityError;

    protected static string $resource = UnitResource::class;

    protected function handleRecordCreation(array $data): \Illuminate\Database\Eloquent\Model
    {
        return $this->runWithUniqueGuard(fn () => parent::handleRecordCreation($data));
    }
}

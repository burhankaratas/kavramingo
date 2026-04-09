<?php

namespace App\Filament\Resources\TopicResource\Pages;

use App\Filament\Resources\TopicResource;
use App\Filament\Support\HandlesIntegrityError;
use Filament\Actions;
use Filament\Resources\Pages\CreateRecord;

class CreateTopic extends CreateRecord
{
    use HandlesIntegrityError;

    protected static string $resource = TopicResource::class;

    protected function handleRecordCreation(array $data): \Illuminate\Database\Eloquent\Model
    {
        return $this->runWithUniqueGuard(fn () => parent::handleRecordCreation($data));
    }
}

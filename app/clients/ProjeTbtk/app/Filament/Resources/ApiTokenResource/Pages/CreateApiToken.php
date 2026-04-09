<?php

namespace App\Filament\Resources\ApiTokenResource\Pages;

use App\Filament\Resources\ApiTokenResource;
use Filament\Actions;
use Filament\Notifications\Notification;
use Filament\Resources\Pages\CreateRecord;

class CreateApiToken extends CreateRecord
{
    protected static string $resource = ApiTokenResource::class;

    protected function mutateFormDataBeforeCreate(array $data): array
    {
        $plainToken = ApiTokenResource::generatePlainToken();
        ApiTokenResource::$plainToken = $plainToken;

        $data['token_hash'] = hash('sha256', $plainToken);

        return $data;
    }

    protected function afterCreate(): void
    {
        Notification::make()
            ->title('Token olusturuldu')
            ->body('Bu token sadece bir kez gorunecek: ' . (ApiTokenResource::$plainToken ?? ''))
            ->success()
            ->persistent()
            ->send();
    }
}

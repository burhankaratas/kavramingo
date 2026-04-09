<?php

namespace App\Filament\Support;

use Filament\Notifications\Notification;
use Illuminate\Database\UniqueConstraintViolationException;

trait HandlesIntegrityError
{
    protected function runWithUniqueGuard(callable $callback)
    {
        try {
            return $callback();
        } catch (UniqueConstraintViolationException $e) {
            Notification::make()
                ->title('Kayit yapilamadi')
                ->body('Ayni sinif/unite numarasi kombinasyonu zaten mevcut. Lutfen farkli bir numara sec.')
                ->danger()
                ->send();

            $this->halt();

            return null;
        }
    }
}

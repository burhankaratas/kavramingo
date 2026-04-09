<?php

namespace App\Console\Commands;

use App\Models\User;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Hash;

class CreateAdminUser extends Command
{
    protected $signature = 'app:create-admin {name} {email} {password}';

    protected $description = 'Create or update an admin user for Filament panel';

    public function handle(): int
    {
        $name = (string) $this->argument('name');
        $email = (string) $this->argument('email');
        $password = (string) $this->argument('password');

        $user = User::query()->where('email', $email)->first();
        if ($user) {
            $user->update([
                'name' => $name,
                'password' => Hash::make($password),
                'is_admin' => true,
            ]);
            $this->info('Admin user updated: ' . $email);
            return self::SUCCESS;
        }

        User::query()->create([
            'name' => $name,
            'email' => $email,
            'password' => Hash::make($password),
            'is_admin' => true,
        ]);

        $this->info('Admin user created: ' . $email);
        return self::SUCCESS;
    }
}

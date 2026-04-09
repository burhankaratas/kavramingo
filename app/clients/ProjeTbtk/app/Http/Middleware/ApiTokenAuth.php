<?php

namespace App\Http\Middleware;

use App\Models\ApiToken;
use App\Support\ApiResponse;
use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class ApiTokenAuth
{
    use ApiResponse;

    public function handle(Request $request, Closure $next, string $requiredScope): Response
    {
        $header = (string) $request->header('Authorization', '');
        if (!str_starts_with($header, 'Bearer ')) {
            return $this->error('UNAUTHORIZED', 'Bearer token gerekli.', [], 401);
        }

        $plainToken = trim(substr($header, 7));
        if ($plainToken === '') {
            return $this->error('UNAUTHORIZED', 'Token bos olamaz.', [], 401);
        }

        $hash = hash('sha256', $plainToken);
        $token = ApiToken::query()
            ->where('token_hash', $hash)
            ->where('is_active', true)
            ->first();

        if (!$token) {
            return $this->error('UNAUTHORIZED', 'Gecersiz token.', [], 401);
        }

        if (!$token->hasScope($requiredScope)) {
            return $this->error('FORBIDDEN', 'Bu islem icin yetkiniz yok.', [], 403);
        }

        $token->forceFill(['last_used_at' => now()])->save();
        $request->attributes->set('api_token', $token);

        return $next($request);
    }
}

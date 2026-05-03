<?php

use Illuminate\Foundation\Application;
use Illuminate\Foundation\Configuration\Exceptions;
use Illuminate\Foundation\Configuration\Middleware;
use Illuminate\Validation\ValidationException;
use Symfony\Component\HttpKernel\Exception\HttpExceptionInterface;

return Application::configure(basePath: dirname(__DIR__))
    ->withCommands([
        \App\Console\Commands\CreateAdminUser::class,
        \App\Console\Commands\ImportContentCsv::class,
        \App\Console\Commands\GenerateMcqFromConcepts::class,
        \App\Console\Commands\GenerateMatchingFromConcepts::class,
        \App\Console\Commands\GenerateFillBlankFromConcepts::class,
    ])
    ->withRouting(
        web: __DIR__.'/../routes/web.php',
        api: __DIR__.'/../routes/api.php',
        commands: __DIR__.'/../routes/console.php',
        health: '/up',
    )
    ->withMiddleware(function (Middleware $middleware) {
        $middleware->alias([
            'api.token' => \App\Http\Middleware\ApiTokenAuth::class,
        ]);

        $middleware->api(prepend: [
            \Illuminate\Http\Middleware\HandleCors::class,
        ]);
    })
    ->withExceptions(function (Exceptions $exceptions): void {
        $exceptions->render(function (ValidationException $e, $request) {
            if (!$request->is('api/*')) {
                return null;
            }

            return response()->json([
                'error_code' => 'VALIDATION_ERROR',
                'message' => 'Gonderilen veri dogrulanamadi.',
                'details' => $e->errors(),
            ], 422);
        });

        $exceptions->render(function (\Throwable $e, $request) {
            if (!$request->is('api/*')) {
                return null;
            }

            $status = 500;
            if ($e instanceof HttpExceptionInterface) {
                $status = $e->getStatusCode();
            }

            $message = $status >= 500 ? 'Sunucu hatasi.' : ($e->getMessage() ?: 'Istek hatasi.');

            return response()->json([
                'error_code' => $status >= 500 ? 'INTERNAL_ERROR' : 'API_ERROR',
                'message' => $message,
                'details' => [],
            ], $status);
        });
    })->create();

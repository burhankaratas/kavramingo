<?php

use Illuminate\Support\Facades\Route;

use App\Http\Controllers\Api\V1\QuestionFeedController;
use App\Http\Controllers\Api\V1\UnitFeedController;

Route::prefix('v1')->middleware('api.token:content:read')->group(function () {
    Route::get('/unites', [UnitFeedController::class, 'index']);
    Route::get('/unites/{unit}', [UnitFeedController::class, 'show']);
    Route::get('/unites/{unit}/konular', [UnitFeedController::class, 'topics']);
    Route::get('/konular/{topic}/kavramlar', [UnitFeedController::class, 'concepts']);

    Route::get('/quiz-feed', [QuestionFeedController::class, 'quizFeed']);
    Route::get('/placement-feed', [QuestionFeedController::class, 'placementFeed']);
});

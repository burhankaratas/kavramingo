<?php

use Illuminate\Support\Facades\Route;

use App\Http\Controllers\Api\ConceptController;
use App\Http\Controllers\Api\UnitController;

// Ünite rotaları
Route::get('/units', [UnitController::class, 'index']);
Route::get('/units/{unit}', [UnitController::class, 'show']);
Route::get('/units/{unit}/concepts', [UnitController::class, 'concepts']);

// Kavram rotaları
Route::get('/concepts', [ConceptController::class, 'index']);
Route::get('/concepts/{concept}', [ConceptController::class, 'show']);
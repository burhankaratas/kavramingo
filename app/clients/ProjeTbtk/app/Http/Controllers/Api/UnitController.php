<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Unit;
use Illuminate\Http\JsonResponse;

class UnitController extends Controller
{
    public function index(): JsonResponse
    {
        $units = Unit::orderBy('order')->get();

        return response()->json([
            'success' => true,
            'data' => $units,
        ]);
    }

    public function show(Unit $unit): JsonResponse
    {
        return response()->json([
            'success' => true,
            'data' => $unit,
        ]);
    }

    public function concepts(Unit $unit): JsonResponse
    {
        $concepts = $unit->concepts()
            ->with(['descriptions', 'examples'])
            ->get();

        return response()->json([
            'success' => true,
            'data' => [
                'unit' => $unit,
                'concepts' => $concepts,
            ],
        ]);
    }
}
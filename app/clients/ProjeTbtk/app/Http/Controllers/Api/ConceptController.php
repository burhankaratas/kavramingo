<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Concept;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class ConceptController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        $query = Concept::with(['unit', 'descriptions', 'examples']);

        // Üniteye göre filtreleme
        if ($request->has('unit_id')) {
            $query->where('unit_id', $request->unit_id);
        }

        $concepts = $query->orderBy('order')->get();

        return response()->json([
            'success' => true,
            'data' => $concepts,
        ]);
    }

    public function show(Concept $concept): JsonResponse
    {
        $concept->load(['unit', 'descriptions', 'examples']);

        return response()->json([
            'success' => true,
            'data' => $concept,
        ]);
    }
}
<?php

namespace App\Http\Controllers\Api\V1;

use App\Http\Controllers\Controller;
use App\Models\Topic;
use App\Models\Unit;
use App\Support\ApiResponse;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class UnitFeedController extends Controller
{
    use ApiResponse;

    public function index(Request $request): JsonResponse
    {
        $grade = $request->integer('grade');
        $perPage = max(1, min($request->integer('per_page', 20), 100));

        $query = Unit::query()->orderBy('grade')->orderBy('unit_no');

        if (in_array($grade, [9, 10, 11, 12], true)) {
            $query->where('grade', $grade);
        }

        return $this->ok($query->paginate($perPage));
    }

    public function show(Unit $unit): JsonResponse
    {
        return $this->ok([
            'id' => $unit->id,
            'grade' => $unit->grade,
            'unit_no' => $unit->unit_no,
            'name' => $unit->name,
            'description' => $unit->description,
        ]);
    }

    public function topics(Unit $unit, Request $request): JsonResponse
    {
        $perPage = max(1, min($request->integer('per_page', 20), 100));

        $topics = $unit->topics()->paginate($perPage);

        return $this->ok($topics);
    }

    public function concepts(Topic $topic, Request $request): JsonResponse
    {
        $perPage = max(1, min($request->integer('per_page', 20), 100));
        $concepts = $topic->concepts()->paginate($perPage);

        return $this->ok($concepts);
    }
}

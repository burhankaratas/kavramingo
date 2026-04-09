<?php

namespace App\Support;

use App\Models\Topic;
use App\Models\Unit;

class UnitTopicResolver
{
    public static function defaultTopicForUnitId(int $unitId): ?Topic
    {
        $unit = Unit::query()->find($unitId);
        if (!$unit) {
            return null;
        }

        $topic = Topic::query()
            ->where('unit_id', $unitId)
            ->orderBy('topic_no')
            ->first();

        if ($topic) {
            return $topic;
        }

        return Topic::query()->create([
            'unit_id' => $unitId,
            'topic_no' => 1,
            'name' => 'Genel',
            'order' => 0,
        ]);
    }
}

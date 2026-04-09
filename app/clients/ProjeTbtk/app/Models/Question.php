<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\HasOne;
use Illuminate\Database\Eloquent\SoftDeletes;

class Question extends Model
{
    use SoftDeletes;

    protected $fillable = [
        'topic_id',
        'quiz_type',
        'difficulty',
        'question_code',
        'prompt',
        'order',
    ];

    public function topic(): BelongsTo
    {
        return $this->belongsTo(Topic::class);
    }

    public function mcq(): HasOne
    {
        return $this->hasOne(McqQuestion::class);
    }

    public function flashcard(): HasOne
    {
        return $this->hasOne(FlashcardQuestion::class);
    }

    public function fillBlank(): HasOne
    {
        return $this->hasOne(FillBlankQuestion::class);
    }

    public function matchingPairs(): HasMany
    {
        return $this->hasMany(MatchingPair::class)->orderBy('order');
    }
}

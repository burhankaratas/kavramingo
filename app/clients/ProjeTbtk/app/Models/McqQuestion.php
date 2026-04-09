<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class McqQuestion extends Model
{
    protected $fillable = [
        'question_id',
        'choice_a',
        'choice_b',
        'choice_c',
        'choice_d',
        'correct_choice',
    ];

    public function question(): BelongsTo
    {
        return $this->belongsTo(Question::class);
    }
}

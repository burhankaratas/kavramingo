<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\SoftDeletes;

class Concept extends Model
{
    use SoftDeletes;

    protected $fillable = [
        'topic_id',
        'name',
        'definition',
        'order',
    ];

    public function topic(): BelongsTo
    {
        return $this->belongsTo(Topic::class);
    }

    public function descriptions(): HasMany
    {
        return $this->hasMany(ConceptDescription::class)->orderBy('order');
    }

    public function examples(): HasMany
    {
        return $this->hasMany(ConceptExample::class)->orderBy('order');
    }
}

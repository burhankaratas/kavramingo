<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Concept extends Model
{
    protected $fillable = [
        'unit_id',
        'name',
        'definition',
        'order',
    ];

    public function unit(): BelongsTo
    {
        return $this->belongsTo(Unit::class);
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
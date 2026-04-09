<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('placement_rules', function (Blueprint $table) {
            $table->id();
            $table->unsignedTinyInteger('grade');
            $table->foreignId('unit_id')->constrained()->cascadeOnDelete();
            $table->unsignedTinyInteger('threshold_percent')->default(70);
            $table->timestamps();

            $table->unique(['grade', 'unit_id'], 'placement_rules_grade_unit_unique');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('placement_rules');
    }
};

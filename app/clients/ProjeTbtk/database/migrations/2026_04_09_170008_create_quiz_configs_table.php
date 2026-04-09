<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('quiz_configs', function (Blueprint $table) {
            $table->id();
            $table->foreignId('unit_id')->constrained()->cascadeOnDelete();
            $table->enum('quiz_type', ['mcq', 'flashcard', 'matching', 'fill_blank']);
            $table->unsignedInteger('question_count')->default(5);
            $table->timestamps();

            $table->unique(['unit_id', 'quiz_type'], 'quiz_configs_unit_type_unique');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('quiz_configs');
    }
};

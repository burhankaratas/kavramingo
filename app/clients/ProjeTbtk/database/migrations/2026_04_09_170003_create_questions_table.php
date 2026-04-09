<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('questions', function (Blueprint $table) {
            $table->id();
            $table->foreignId('topic_id')->constrained()->cascadeOnDelete();
            $table->enum('quiz_type', ['mcq', 'flashcard', 'matching', 'fill_blank']);
            $table->enum('difficulty', ['easy', 'medium', 'hard'])->default('easy');
            $table->string('question_code')->unique();
            $table->text('prompt')->nullable();
            $table->unsignedInteger('order')->default(0);
            $table->timestamps();
            $table->softDeletes();

            $table->index(['topic_id', 'quiz_type'], 'questions_topic_type_idx');
            $table->index(['quiz_type', 'difficulty'], 'questions_type_difficulty_idx');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('questions');
    }
};

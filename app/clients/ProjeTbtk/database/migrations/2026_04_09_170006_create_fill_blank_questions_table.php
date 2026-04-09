<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('fill_blank_questions', function (Blueprint $table) {
            $table->id();
            $table->foreignId('question_id')->unique()->constrained('questions')->cascadeOnDelete();
            $table->text('sentence_template');
            $table->string('answer_text');
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('fill_blank_questions');
    }
};

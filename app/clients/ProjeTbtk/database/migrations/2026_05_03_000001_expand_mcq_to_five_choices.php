<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('mcq_questions', function (Blueprint $table) {
            $table->text('choice_e')->nullable()->after('choice_d');
        });

        DB::statement("ALTER TABLE mcq_questions MODIFY correct_choice ENUM('A','B','C','D','E') NOT NULL");
    }

    public function down(): void
    {
        DB::statement("ALTER TABLE mcq_questions MODIFY correct_choice ENUM('A','B','C','D') NOT NULL");

        Schema::table('mcq_questions', function (Blueprint $table) {
            $table->dropColumn('choice_e');
        });
    }
};

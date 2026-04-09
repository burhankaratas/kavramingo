<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('units', function (Blueprint $table) {
            $table->unsignedTinyInteger('grade')->default(9)->after('id');
            $table->unsignedInteger('unit_no')->default(1)->after('grade');
            $table->softDeletes();

            $table->unique(['grade', 'unit_no'], 'units_grade_unit_no_unique');
        });
    }

    public function down(): void
    {
        Schema::table('units', function (Blueprint $table) {
            $table->dropUnique('units_grade_unit_no_unique');
            $table->dropSoftDeletes();
            $table->dropColumn(['grade', 'unit_no']);
        });
    }
};

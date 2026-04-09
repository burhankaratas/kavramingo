<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('concepts', function (Blueprint $table) {
            $table->foreignId('topic_id')->nullable()->after('unit_id')->constrained()->cascadeOnDelete();
            $table->softDeletes();
        });

        Schema::table('concepts', function (Blueprint $table) {
            $table->dropConstrainedForeignId('unit_id');
            $table->dropColumn('unit_id');
            $table->index(['topic_id', 'order'], 'concepts_topic_order_idx');
        });

        DB::statement('ALTER TABLE concepts MODIFY topic_id BIGINT UNSIGNED NOT NULL');
    }

    public function down(): void
    {
        Schema::table('concepts', function (Blueprint $table) {
            $table->dropIndex('concepts_topic_order_idx');
            $table->dropConstrainedForeignId('topic_id');
            $table->dropSoftDeletes();
            $table->foreignId('unit_id')->constrained()->cascadeOnDelete();
        });
    }
};

<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        if (!Schema::hasColumn('concepts', 'topic_id')) {
            if (Schema::hasColumn('concepts', 'unit_id')) {
                Schema::table('concepts', function (Blueprint $table) {
                    $table->foreignId('topic_id')->nullable()->after('unit_id')->constrained()->cascadeOnDelete();
                });
            } else {
                Schema::table('concepts', function (Blueprint $table) {
                    $table->foreignId('topic_id')->nullable()->constrained()->cascadeOnDelete();
                });
            }
        }

        if (!Schema::hasColumn('concepts', 'deleted_at')) {
            Schema::table('concepts', function (Blueprint $table) {
                $table->softDeletes();
            });
        }

        if (Schema::hasColumn('concepts', 'unit_id')) {
            Schema::table('concepts', function (Blueprint $table) {
                $table->dropConstrainedForeignId('unit_id');
                $table->dropColumn('unit_id');
            });
        }

        $hasIndex = DB::selectOne("SHOW INDEX FROM concepts WHERE Key_name = 'concepts_topic_order_idx'");
        if (!$hasIndex) {
            Schema::table('concepts', function (Blueprint $table) {
                $table->index(['topic_id', 'order'], 'concepts_topic_order_idx');
            });
        }

        DB::statement('ALTER TABLE concepts MODIFY topic_id BIGINT UNSIGNED NOT NULL');
    }

    public function down(): void
    {
        if (Schema::hasColumn('concepts', 'topic_id')) {
            $hasIndex = DB::selectOne("SHOW INDEX FROM concepts WHERE Key_name = 'concepts_topic_order_idx'");
            if ($hasIndex) {
                Schema::table('concepts', function (Blueprint $table) {
                    $table->dropIndex('concepts_topic_order_idx');
                });
            }

            Schema::table('concepts', function (Blueprint $table) {
                $table->dropConstrainedForeignId('topic_id');
            });
        }

        if (Schema::hasColumn('concepts', 'deleted_at')) {
            Schema::table('concepts', function (Blueprint $table) {
                $table->dropSoftDeletes();
            });
        }

        if (!Schema::hasColumn('concepts', 'unit_id')) {
            Schema::table('concepts', function (Blueprint $table) {
                $table->foreignId('unit_id')->constrained()->cascadeOnDelete();
            });
        }
    }
};

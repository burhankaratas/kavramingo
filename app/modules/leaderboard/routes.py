"""
app/modules/leaderboard/routes.py
──────────────────────────────────
Liderlik tablosu: DB'den gerçek veri, dönem + sınıf filtresi.

Sorgu parametreleri:
  period : all (varsayılan) | daily | weekly | monthly
  grade  : all (varsayılan) | 9 | 10 | 11 | 12

Dönem skoru:
  all     → users.total_score
  diğerleri → scores tablosundan o dönemki SUM(points)

Doğruluk % → tüm zamanlar (quiz_answers tablosundan)
Seri       → users.streak kolonu (check_badges() her quiz sonunda günceller)

Top-50 dışındaki kullanıcı: ayrı sorgu ile sırası + istatistikleri bulunur,
sayfanın altına yapıştırılmış bant olarak gösterilir.
"""

from datetime import datetime, timedelta

from flask import render_template, request
from flask_login import login_required, current_user

from app.extensions import mysql
from app.modules.leaderboard import leaderboard_bp

# ── Sabitler ──────────────────────────────────────────────────────────────────

PERIOD_LABELS = {
    "all":     "Tüm Zamanlar",
    "monthly": "Bu Ay",
    "weekly":  "Bu Hafta",
    "daily":   "Bugün",
}

VALID_PERIODS = set(PERIOD_LABELS.keys())
VALID_GRADES  = {"9", "10", "11", "12"}

LIMIT = 50


# ── Yardımcılar ───────────────────────────────────────────────────────────────

def _period_since(period: str) -> datetime | None:
    """Dönem başlangıcını UTC datetime olarak döndürür; 'all' için None."""
    now = datetime.utcnow()
    if period == "daily":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    if period == "weekly":
        return now - timedelta(days=7)
    if period == "monthly":
        return now - timedelta(days=30)
    return None  # all-time


def _build_entries(rows, current_user_id: int) -> tuple[list, bool]:
    """
    DB satırlarını template'e uygun dict listesine çevirir.
    Döndürür: (entries, user_in_top)
    """
    entries = []
    user_in_top = False
    for i, row in enumerate(rows):
        is_you = (row["id"] == current_user_id)
        if is_you:
            user_in_top = True
        entries.append({
            "rank":     i + 1,
            "id":       row["id"],
            "name":     row["name"],
            "grade":    row["grade"] or 0,
            "score":    row["score"] or 0,
            "streak":   row["streak"] or 0,
            "accuracy": row["accuracy"] or 0,
            "you":      is_you,
        })
    return entries, user_in_top


def _fetch_top(cur, since, grade_filter) -> list:
    """
    Top-LIMIT listesini çeker.
    since=None → all-time (users.total_score),
    since=datetime → o tarihten bu yana scores SUM.
    """
    grade_cond   = "AND u.grade = %s" if grade_filter else ""
    grade_params = [int(grade_filter)] if grade_filter else []

    if since is None:
        # ── All-time ──────────────────────────────────────────────────────
        sql = f"""
            SELECT
                u.id, u.name, u.grade,
                u.total_score                        AS score,
                u.streak,
                COALESCE(ROUND(
                    SUM(CASE WHEN qa.is_correct=1 THEN 1 ELSE 0 END) * 100.0
                    / NULLIF(COUNT(qa.id), 0)
                ), 0)                                AS accuracy
            FROM users u
            LEFT JOIN quiz_sessions qs
                   ON qs.user_id = u.id
                  AND qs.finished_at IS NOT NULL
            LEFT JOIN quiz_answers qa ON qa.session_id = qs.id
            WHERE 1=1 {grade_cond}
            GROUP BY u.id, u.name, u.grade, u.total_score, u.streak
            ORDER BY score DESC
            LIMIT {LIMIT}
        """
        cur.execute(sql, grade_params)
    else:
        # ── Dönem tabanlı ─────────────────────────────────────────────────
        sql = f"""
            SELECT
                u.id, u.name, u.grade,
                COALESCE(SUM(sc.points), 0)          AS score,
                u.streak,
                COALESCE(ROUND(
                    SUM(CASE WHEN qa.is_correct=1 THEN 1 ELSE 0 END) * 100.0
                    / NULLIF(COUNT(qa.id), 0)
                ), 0)                                AS accuracy
            FROM users u
            LEFT JOIN scores sc
                   ON sc.user_id = u.id
                  AND sc.earned_at >= %s
            LEFT JOIN quiz_sessions qs
                   ON qs.user_id = u.id
                  AND qs.finished_at IS NOT NULL
                  AND qs.finished_at >= %s
            LEFT JOIN quiz_answers qa ON qa.session_id = qs.id
            WHERE 1=1 {grade_cond}
            GROUP BY u.id, u.name, u.grade, u.streak
            ORDER BY score DESC
            LIMIT {LIMIT}
        """
        cur.execute(sql, [since, since] + grade_params)

    return cur.fetchall()


def _fetch_user_stats(cur, since, grade_filter, user_id: int) -> dict | None:
    """
    Kullanıcının kendi istatistikleri ve sıralamasını döndürür.
    Top-50 dışındaysa kullanılır.
    """
    grade_cond   = "AND u.grade = %s" if grade_filter else ""
    grade_params = [int(grade_filter)] if grade_filter else []

    if since is None:
        # ── All-time: kullanıcı skoru ─────────────────────────────────────
        cur.execute("""
            SELECT
                u.id, u.name, u.grade,
                u.total_score AS score, u.streak,
                COALESCE(ROUND(
                    SUM(CASE WHEN qa.is_correct=1 THEN 1 ELSE 0 END) * 100.0
                    / NULLIF(COUNT(qa.id), 0)
                ), 0) AS accuracy
            FROM users u
            LEFT JOIN quiz_sessions qs
                   ON qs.user_id = u.id AND qs.finished_at IS NOT NULL
            LEFT JOIN quiz_answers qa ON qa.session_id = qs.id
            WHERE u.id = %s
            GROUP BY u.id, u.name, u.grade, u.total_score, u.streak
        """, [user_id])
        u_row = cur.fetchone()
        if not u_row:
            return None

        # Kaçıncı sırada?
        rank_grade_cond = "AND grade = %s" if grade_filter else ""
        rank_sql = f"""
            SELECT COUNT(*) + 1 AS user_rank
            FROM users
            WHERE total_score > %s {rank_grade_cond}
        """
        cur.execute(rank_sql, [u_row["score"]] + grade_params)
        rank_row = cur.fetchone()

    else:
        # ── Dönem: kullanıcı skoru ────────────────────────────────────────
        cur.execute("""
            SELECT
                u.id, u.name, u.grade,
                COALESCE(SUM(sc.points), 0)  AS score,
                u.streak,
                COALESCE(ROUND(
                    SUM(CASE WHEN qa.is_correct=1 THEN 1 ELSE 0 END) * 100.0
                    / NULLIF(COUNT(qa.id), 0)
                ), 0) AS accuracy
            FROM users u
            LEFT JOIN scores sc
                   ON sc.user_id = u.id AND sc.earned_at >= %s
            LEFT JOIN quiz_sessions qs
                   ON qs.user_id = u.id
                  AND qs.finished_at IS NOT NULL AND qs.finished_at >= %s
            LEFT JOIN quiz_answers qa ON qa.session_id = qs.id
            WHERE u.id = %s
            GROUP BY u.id, u.name, u.grade, u.streak
        """, [since, since, user_id])
        u_row = cur.fetchone()
        if not u_row:
            return None

        # Kaçıncı sırada? (aynı dönemde kaç kişi daha fazla puan kazandı)
        rank_grade_cond = "AND uu.grade = %s" if grade_filter else ""
        rank_sql = f"""
            SELECT COUNT(*) + 1 AS user_rank
            FROM (
                SELECT user_id, COALESCE(SUM(points), 0) AS s
                FROM scores
                WHERE earned_at >= %s
                GROUP BY user_id
            ) t
            JOIN users uu ON uu.id = t.user_id
            WHERE t.s > %s {rank_grade_cond}
        """
        cur.execute(rank_sql, [since, u_row["score"]] + grade_params)
        rank_row = cur.fetchone()

    user_rank = rank_row["user_rank"] if rank_row else LIMIT + 1
    return {
        "rank":     user_rank,
        "id":       u_row["id"],
        "name":     u_row["name"],
        "grade":    u_row["grade"] or 0,
        "score":    u_row["score"] or 0,
        "streak":   u_row["streak"] or 0,
        "accuracy": u_row["accuracy"] or 0,
        "you":      True,
    }


# ── Route ─────────────────────────────────────────────────────────────────────

@leaderboard_bp.route("/")
@login_required
def index():
    period       = request.args.get("period", "all")
    grade_filter = request.args.get("grade", "all")

    if period not in VALID_PERIODS:
        period = "all"
    if grade_filter not in VALID_GRADES:
        grade_filter = None  # all

    since = _period_since(period)

    cur = mysql.connection.cursor()

    top_rows          = _fetch_top(cur, since, grade_filter)
    entries, user_in_top = _build_entries(top_rows, current_user.id)

    # Kullanıcı top-50 dışındaysa alta yapıştırılacak satır
    sticky_user = None
    if not user_in_top:
        sticky_user = _fetch_user_stats(cur, since, grade_filter, current_user.id)

    cur.close()

    top3 = entries[:3]
    rest = entries[3:]

    return render_template(
        "leaderboard/index.html",
        entries      = entries,
        top3         = top3,
        rest         = rest,
        sticky_user  = sticky_user,
        grade_filter = grade_filter or "all",
        period       = period,
        period_label = PERIOD_LABELS[period],
        period_labels= PERIOD_LABELS,
    )

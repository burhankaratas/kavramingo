from flask import render_template
from flask_login import current_user, login_required

from app.clients.kavram_api import get_unite

from app.modules.dashboard import dashboard_bp
from app.extensions import mysql
from app.services.badge_service import get_user_streak


# ── Yardımcı: API'den ünite bilgisi ──────────────────────────────────────────

def _load_unit_info(unit_id: int) -> dict | None:
    payload = get_unite(unit_id)
    if not payload:
        return None

    return {
        "unit_id": unit_id,
        "name": payload.get("name", f"Unite {unit_id}"),
        "number": payload.get("unit_no", 1),
        "grade": payload.get("grade", current_user.grade or 9),
        "total_questions": 0,
    }


@dashboard_bp.route("/")
def index():
    if not current_user.is_authenticated:
        return render_template("landing/index.html")
    # ── Rozet verisi (DB) ──────────────────────────────────────────────────
    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM badges ORDER BY condition_value")
    all_badges = cur.fetchall()

    cur.execute(
        "SELECT badge_id, earned_at FROM user_badges WHERE user_id = %s",
        (current_user.id,)
    )
    earned_map = {r["badge_id"]: r["earned_at"] for r in cur.fetchall()}

    cur.execute("SELECT total_score, daily_goal FROM users WHERE id = %s", (current_user.id,))
    user_row = cur.fetchone()
    total_score = user_row["total_score"] if user_row else 0
    daily_goal  = user_row["daily_goal"]  if user_row else 5

    cur.execute(
        "SELECT COUNT(*) AS cnt FROM quiz_sessions WHERE user_id=%s AND finished_at IS NOT NULL",
        (current_user.id,)
    )
    quiz_count = cur.fetchone()["cnt"]

    cur.execute(
        "SELECT COUNT(*) AS cnt FROM progress WHERE user_id=%s AND status='completed'",
        (current_user.id,)
    )
    unit_count = cur.fetchone()["cnt"]

    cur.execute("""
        SELECT COUNT(*) AS cnt FROM quiz_sessions
        WHERE user_id = %s AND finished_at IS NOT NULL
        AND DATE(finished_at) = UTC_DATE()
    """, (current_user.id,))
    daily_done = cur.fetchone()["cnt"]

    cur.close()

    streak = get_user_streak(current_user.id, mysql)

    user_vals = {
        "score":         total_score,
        "quiz_count":    quiz_count,
        "unit_complete": unit_count,
        "streak":        streak,
    }

    # Kategori renk haritası
    CAT_COLORS = {
        "baslangic":   "#4361EE",
        "seri":        "#D9730D",
        "quiz":        "#7209B7",
        "mukemmellik": "#059669",
        "unite":       "#0099B8",
    }

    # Tüm rozetlere progress ekle
    enriched = []
    for b in all_badges:
        bid  = b["id"]
        earned = bid in earned_map
        cv   = b["condition_value"] or 1
        cur_val = user_vals.get(b["condition_type"], 0)
        enriched.append({
            **b,
            "earned":       earned,
            "earned_at":    earned_map.get(bid),
            "current_val":  cur_val,
            "progress_pct": min(100, int(cur_val / cv * 100)),
            "cat_color":    CAT_COLORS.get(b.get("category", ""), "#4361EE"),
        })

    # İlk 6: önce kazanılanlar (son kazanılan önce), sonra en yakın kilitliler
    earned_list = sorted(
        [b for b in enriched if b["earned"]],
        key=lambda x: x["earned_at"] or "",
        reverse=True
    )
    locked_list = sorted(
        [b for b in enriched if not b["earned"]],
        key=lambda x: -x["progress_pct"]
    )
    badges_preview = (earned_list + locked_list)[:6]

    # ── Current Unit: kullanıcının en son oynadığı ünite ─────────────────────
    UNIT_QUIZ_TARGET = 20  # Bu kadar quiz = %100

    cur2 = mysql.connection.cursor()

    cur2.execute("""
        SELECT unite_id FROM quiz_sessions
        WHERE user_id = %s AND finished_at IS NOT NULL
        ORDER BY finished_at DESC
        LIMIT 1
    """, (current_user.id,))
    last_row = cur2.fetchone()

    current_unit = None
    if last_row:
        last_unit_id = last_row["unite_id"]
        unit_info = _load_unit_info(last_unit_id)
        if unit_info:
            cur2.execute("""
                SELECT COUNT(*) AS cnt FROM quiz_sessions
                WHERE user_id = %s AND unite_id = %s AND finished_at IS NOT NULL
            """, (current_user.id, last_unit_id))
            unit_sessions = cur2.fetchone()["cnt"]
            progress_pct = min(100, int(unit_sessions / UNIT_QUIZ_TARGET * 100))
            current_unit = {
                **unit_info,
                "quiz_done":    unit_sessions,
                "quiz_target":  UNIT_QUIZ_TARGET,
                "progress":     progress_pct,
                "completed":    progress_pct >= 100,
            }

    cur2.close()

    return render_template(
        "dashboard/index.html",
        current_unit=current_unit,
        badges=badges_preview,
        earned_total=len(earned_map),
        total_badges=len(all_badges),
        streak=streak,
        daily_done=daily_done,
        daily_goal=daily_goal,
        quiz_ready=current_unit is not None,
    )

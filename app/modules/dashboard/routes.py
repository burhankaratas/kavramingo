from flask import render_template
from flask_login import current_user, login_required

from app.modules.dashboard import dashboard_bp
from app.extensions import mysql
from app.services.badge_service import get_user_streak


@dashboard_bp.route("/")
@login_required
def index():
    # ── Rozet verisi (DB) ──────────────────────────────────────────────────
    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM badges ORDER BY condition_value")
    all_badges = cur.fetchall()

    cur.execute(
        "SELECT badge_id, earned_at FROM user_badges WHERE user_id = %s",
        (current_user.id,)
    )
    earned_map = {r["badge_id"]: r["earned_at"] for r in cur.fetchall()}

    cur.execute("SELECT total_score FROM users WHERE id = %s", (current_user.id,))
    user_row = cur.fetchone()
    total_score = user_row["total_score"] if user_row else 0

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

    # TODO: aşağıdakileri DB/API'den al
    current_unit = {
        "unit_id": 1,
        "quiz_type": "multiple_choice",
        "number": 1,
        "name": "Bilgi ve İnanç",
        "current_topic": "Tevhid Kavramı",
        "progress": 40,
        "done_topics": 8,
        "total_topics": 20,
        "topics": [
            {"name": "Bilgi Nedir?",            "status": "done"},
            {"name": "İnanç ve Bilgi İlişkisi", "status": "done"},
            {"name": "Tevhid Kavramı",          "status": "active"},
            {"name": "İman Esasları",           "status": "upcoming"},
            {"name": "Allah'ın Sıfatları",      "status": "upcoming"},
            {"name": "Şirk ve Sonuçları",       "status": "locked"},
        ],
    }

    return render_template(
        "dashboard/index.html",
        current_unit=current_unit,
        badges=badges_preview,
        earned_total=len(earned_map),
        total_badges=len(all_badges),
        streak=streak,
        daily_done=3,
        daily_goal=5,
        quiz_ready=True,
    )

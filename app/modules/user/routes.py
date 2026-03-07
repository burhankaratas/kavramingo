from flask import render_template
from flask_login import login_required, current_user

from app.modules.user import user_bp
from app.extensions import mysql
from app.services.badge_service import get_user_streak

# Kategori meta verisi — sıralı
CATEGORY_ORDER = ["baslangic", "seri", "quiz", "mukemmellik", "unite"]

CATEGORY_META = {
    "baslangic":   {"label": "Başlangıç",   "icon": "bi-rocket-takeoff-fill", "color": "#4361EE"},
    "seri":        {"label": "Seri",         "icon": "bi-fire",                "color": "#D9730D"},
    "quiz":        {"label": "Quiz Ustası",  "icon": "bi-mortarboard-fill",    "color": "#7209B7"},
    "mukemmellik": {"label": "Mükemmellik",  "icon": "bi-gem",                 "color": "#059669"},
    "unite":       {"label": "Ünite",        "icon": "bi-collection-fill",     "color": "#0099B8"},
}


@user_bp.route("/profile")
@login_required
def profile():
    return render_template("user/profile.html")


@user_bp.route("/settings")
@login_required
def settings():
    return render_template("user/settings.html")


@user_bp.route("/rozetler")
@login_required
def badges():
    cur = mysql.connection.cursor()

    # Tüm rozetleri çek
    cur.execute("""
        SELECT * FROM badges
        ORDER BY FIELD(category,'baslangic','seri','quiz','mukemmellik','unite'), condition_value
    """)
    all_badges = cur.fetchall()

    # Kullanıcının kazandığı rozetler (badge_id → earned_at)
    cur.execute("""
        SELECT badge_id, earned_at
        FROM user_badges
        WHERE user_id = %s
    """, (current_user.id,))
    earned_map = {r["badge_id"]: r["earned_at"] for r in cur.fetchall()}

    # Kullanıcı istatistikleri (ilerleme çubuğu için)
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

    # Rozetleri kategoriye göre grupla + ilerleme ekle
    categories = []
    for cat_key in CATEGORY_ORDER:
        meta = CATEGORY_META.get(cat_key, {})
        cat_badges = [b for b in all_badges if b.get("category") == cat_key]

        badges_out = []
        for b in cat_badges:
            bid = b["id"]
            earned = bid in earned_map
            cv = b["condition_value"] or 1
            current_val = user_vals.get(b["condition_type"], 0)
            progress_pct = min(100, int(current_val / cv * 100))
            badges_out.append({
                **b,
                "earned":    earned,
                "earned_at": earned_map.get(bid),
                "current_val":   current_val,
                "progress_pct":  progress_pct,
            })

        categories.append({
            "key":          cat_key,
            "label":        meta.get("label", cat_key),
            "icon":         meta.get("icon", "bi-award-fill"),
            "color":        meta.get("color", "#4361EE"),
            "badges":       badges_out,
            "earned_count": sum(1 for b in badges_out if b["earned"]),
            "total_count":  len(badges_out),
        })

    return render_template(
        "user/badges.html",
        categories=categories,
        earned_total=len(earned_map),
        total_badges=len(all_badges),
        streak=streak,
        user_vals=user_vals,
    )

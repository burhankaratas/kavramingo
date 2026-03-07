"""
app/modules/progress/routes.py
──────────────────────────────
İlerleme Takibi — kullanıcının tüm ünitelerdeki quiz oturum sayısını gösterir.

GET /ilerleme/    → sınıfa göre gruplu ünite kartları + progress barlar
"""

import json
import os

from flask import render_template
from flask_login import current_user, login_required

from app.modules.progress import progress_bp
from app.extensions import mysql

# ── Sabitler ─────────────────────────────────────────────────────────────────

UNIT_QUIZ_TARGET = 20   # Bu kadar oturum = %100 tamamlandı

# Sınıf renk/etiket meta verisi (library.routes ile aynı)
GRADE_META = {
    9:  {"color": "#4361EE", "bg": "#EEF1FD", "label": "9. Sınıf"},
    10: {"color": "#7209B7", "bg": "#F5F3FF", "label": "10. Sınıf"},
    11: {"color": "#D9730D", "bg": "#FFF4E0", "label": "11. Sınıf"},
    12: {"color": "#059669", "bg": "#ECFDF5", "label": "12. Sınıf"},
}


def _load_all_units() -> list[dict]:
    """Tüm grade JSON'larından ünite listesini (grade bilgisiyle) döndürür."""
    base = os.path.join(os.path.dirname(__file__), "..", "..", "data", "quiz")
    units = []
    for grade in [9, 10, 11, 12]:
        path = os.path.join(base, f"grade_{grade}.json")
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            for idx, u in enumerate(data.get("units", [])):
                units.append({
                    "unit_id": u["unit_id"],
                    "name":    u.get("name", f"Ünite {u['unit_id']}"),
                    "number":  idx + 1,
                    "grade":   grade,
                })
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            pass
    return units


@progress_bp.route("/")
@login_required
def index():
    uid         = current_user.id
    user_grade  = current_user.grade or 9
    all_units   = _load_all_units()

    if not all_units:
        return render_template(
            "progress/index.html",
            grouped=[],
            grade_meta=GRADE_META,
            user_grade=user_grade,
            total_units=0,
            completed_units=0,
            total_sessions=0,
        )

    # ── DB: kullanıcının her ünite için tamamlanan oturum sayısı ─────────────
    unit_ids = [u["unit_id"] for u in all_units]
    fmt      = ",".join(["%s"] * len(unit_ids))

    cur = mysql.connection.cursor()
    cur.execute(f"""
        SELECT unite_id, COUNT(*) AS cnt
        FROM quiz_sessions
        WHERE user_id = %s
          AND finished_at IS NOT NULL
          AND unite_id IN ({fmt})
        GROUP BY unite_id
    """, [uid] + unit_ids)
    session_map = {r["unite_id"]: r["cnt"] for r in cur.fetchall()}
    cur.close()

    # ── Ünitelere ilerleme ekle ───────────────────────────────────────────────
    enriched = []
    for u in all_units:
        done = session_map.get(u["unit_id"], 0)
        pct  = min(100, int(done / UNIT_QUIZ_TARGET * 100))
        enriched.append({
            **u,
            "sessions_done": done,
            "sessions_target": UNIT_QUIZ_TARGET,
            "progress_pct": pct,
            "completed": pct >= 100,
            "started":   done > 0,
        })

    # ── Sınıfa göre grupla — kullanıcının kendi sınıfı en üstte ─────────────
    grade_order = [user_grade] + [g for g in [9, 10, 11, 12] if g != user_grade]
    grouped = []
    for g in grade_order:
        grade_units = [u for u in enriched if u["grade"] == g]
        if not grade_units:
            continue
        completed_in_grade = sum(1 for u in grade_units if u["completed"])
        grouped.append({
            "grade":          g,
            "meta":           GRADE_META[g],
            "units":          grade_units,
            "is_user_grade":  g == user_grade,
            "completed":      completed_in_grade,
            "total":          len(grade_units),
        })

    total_completed  = sum(1 for u in enriched if u["completed"])
    total_sessions   = sum(u["sessions_done"] for u in enriched)

    return render_template(
        "progress/index.html",
        grouped=grouped,
        grade_meta=GRADE_META,
        user_grade=user_grade,
        total_units=len(enriched),
        completed_units=total_completed,
        total_sessions=total_sessions,
    )

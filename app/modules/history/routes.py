"""
app/modules/history/routes.py
──────────────────────────────
Quiz Geçmişi — kullanıcının tüm quiz oturumlarını listeler.

GET /gecmis/    → tarih sıralı oturum listesi (max 50), client-side filtre
"""

import json
import os
from datetime import datetime

from flask import render_template
from flask_login import current_user, login_required

from app.modules.history import history_bp
from app.extensions import mysql


QUIZ_TYPE_META = {
    "multiple_choice": {"label": "Çoktan Seçmeli", "icon": "bi-check2-circle",  "color": "#4361EE", "bg": "#EEF1FD"},
    "flashcard":       {"label": "Flashcard",       "icon": "bi-card-text",       "color": "#D9730D", "bg": "#FFF4E0"},
    "matching":        {"label": "Eşleştirme",      "icon": "bi-shuffle",         "color": "#06D6A0", "bg": "#ECFDF5"},
    "fill_blank":      {"label": "Boşluk Doldurma", "icon": "bi-pencil-fill",     "color": "#7209B7", "bg": "#F5F3FF"},
}

GRADE_META = {
    9:  {"color": "#4361EE", "bg": "#EEF1FD", "label": "9. Sınıf"},
    10: {"color": "#7209B7", "bg": "#F5F3FF", "label": "10. Sınıf"},
    11: {"color": "#D9730D", "bg": "#FFF4E0", "label": "11. Sınıf"},
    12: {"color": "#059669", "bg": "#ECFDF5", "label": "12. Sınıf"},
}

SESSION_LIMIT = 50


def _load_unit_map() -> dict:
    """Tüm grade JSON'larından {unit_id: {name, grade, number}} döndürür."""
    base = os.path.join(os.path.dirname(__file__), "..", "..", "data", "quiz")
    unit_map = {}
    for grade in [9, 10, 11, 12]:
        path = os.path.join(base, f"grade_{grade}.json")
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            for idx, u in enumerate(data.get("units", [])):
                unit_map[u["unit_id"]] = {
                    "name":   u.get("name", f"Ünite {u['unit_id']}"),
                    "grade":  grade,
                    "number": idx + 1,
                }
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            pass
    return unit_map


def _time_ago(dt: datetime) -> str:
    if dt is None:
        return ""
    now   = datetime.utcnow()
    diff  = now - dt
    mins  = int(diff.total_seconds() // 60)
    if mins < 2:   return "Az önce"
    if mins < 60:  return f"{mins} dakika önce"
    hours = mins // 60
    if hours < 24: return f"{hours} saat önce"
    days  = hours // 24
    if days == 1:  return "Dün"
    if days < 7:   return f"{days} gün önce"
    weeks = days // 7
    if weeks == 1: return "1 hafta önce"
    return f"{weeks} hafta önce"


@history_bp.route("/")
@login_required
def index():
    uid      = current_user.id
    unit_map = _load_unit_map()

    cur = mysql.connection.cursor()

    # ── En fazla 50 tamamlanmış oturum ───────────────────────────────────────
    cur.execute("""
        SELECT
            qs.id,
            qs.unite_id,
            qs.quiz_type,
            qs.started_at,
            qs.finished_at,
            COALESCE(sc.points, 0)                          AS xp,
            COUNT(qa.id)                                    AS total_q,
            COALESCE(SUM(qa.is_correct), 0)                 AS correct_q
        FROM quiz_sessions qs
        LEFT JOIN scores sc    ON sc.source_quiz_id = qs.id
        LEFT JOIN quiz_answers qa ON qa.session_id  = qs.id
        WHERE qs.user_id = %s AND qs.finished_at IS NOT NULL
        GROUP BY qs.id, qs.unite_id, qs.quiz_type, qs.started_at, qs.finished_at, sc.points
        ORDER BY qs.finished_at DESC
        LIMIT %s
    """, (uid, SESSION_LIMIT))
    rows = cur.fetchall()

    # ── Özet istatistikler ───────────────────────────────────────────────────
    cur.execute("""
        SELECT COUNT(*) AS total_sessions,
               COALESCE(SUM(sc.points), 0) AS total_xp
        FROM quiz_sessions qs
        LEFT JOIN scores sc ON sc.source_quiz_id = qs.id
        WHERE qs.user_id = %s AND qs.finished_at IS NOT NULL
    """, (uid,))
    summary = cur.fetchone()

    cur.execute("""
        SELECT COALESCE(ROUND(
            SUM(qa.is_correct) * 100.0 / NULLIF(COUNT(qa.id), 0)
        ), 0) AS acc
        FROM quiz_answers qa
        JOIN quiz_sessions qs ON qs.id = qa.session_id
        WHERE qs.user_id = %s AND qs.finished_at IS NOT NULL
    """, (uid,))
    avg_acc = int(cur.fetchone()["acc"] or 0)

    cur.close()

    # ── Oturumları zenginleştir ──────────────────────────────────────────────
    sessions = []
    for r in rows:
        qt_key  = r["quiz_type"] or "multiple_choice"
        qt_meta = QUIZ_TYPE_META.get(qt_key, QUIZ_TYPE_META["multiple_choice"])
        uid_val = r["unite_id"]
        unit    = unit_map.get(uid_val, {})
        grade   = unit.get("grade", current_user.grade or 9)
        gm      = GRADE_META.get(grade, GRADE_META[9])
        total_q   = int(r["total_q"]   or 0)
        correct_q = int(r["correct_q"] or 0)
        acc = int(correct_q / total_q * 100) if total_q > 0 else None

        sessions.append({
            "id":         r["id"],
            "unit_name":  unit.get("name", f"Ünite {uid_val}"),
            "unit_number":unit.get("number", ""),
            "grade":      grade,
            "grade_meta": gm,
            "qt_key":     qt_key,
            "qt_label":   qt_meta["label"],
            "qt_icon":    qt_meta["icon"],
            "qt_color":   qt_meta["color"],
            "qt_bg":      qt_meta["bg"],
            "xp":         int(r["xp"] or 0),
            "total_q":    total_q,
            "correct_q":  correct_q,
            "accuracy":   acc,
            "time_ago":   _time_ago(r["finished_at"]),
            "date_str":   r["finished_at"].strftime("%-d %b %Y") if r["finished_at"] else "",
        })

    # Filtre barı için benzersiz üniteler (oynananlar)
    seen_units = {}
    for s in sessions:
        key = s["unit_name"]
        if key not in seen_units:
            seen_units[key] = {"name": s["unit_name"], "grade": s["grade"]}
    filter_units = sorted(seen_units.values(), key=lambda x: (x["grade"], x["name"]))

    return render_template(
        "history/index.html",
        sessions=sessions,
        quiz_type_meta=QUIZ_TYPE_META,
        filter_units=filter_units,
        total_sessions=summary["total_sessions"],
        total_xp=int(summary["total_xp"] or 0),
        avg_accuracy=avg_acc,
        session_limit=SESSION_LIMIT,
    )

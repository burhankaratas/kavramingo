"""
app/modules/library/routes.py
─────────────────────────────
Unite Kutuphanesi - API tabanli listeleme.

GET /library/            -> tum uniteler
GET /library/?grade=9    -> sadece 9. sinif uniteleri
"""

from flask import render_template, request
from flask_login import login_required

from app.clients.kavram_api import get_unites
from app.modules.library import library_bp


QUIZ_TYPES = [
    {"key": "multiple_choice", "label": "Coktan Secmeli", "icon": "bi-check2-circle", "color": "#4361EE"},
    {"key": "flashcard", "label": "Flashcard", "icon": "bi-card-text", "color": "#D9730D"},
    {"key": "matching", "label": "Eslestirme", "icon": "bi-shuffle", "color": "#06D6A0"},
    {"key": "fill_blank", "label": "Bosluk Doldurma", "icon": "bi-pencil-fill", "color": "#7209B7"},
]

GRADE_META = {
    9: {"color": "#4361EE", "bg": "#EEF1FD", "label": "9. Sinif"},
    10: {"color": "#7209B7", "bg": "#F5F3FF", "label": "10. Sinif"},
    11: {"color": "#D9730D", "bg": "#FFF4E0", "label": "11. Sinif"},
    12: {"color": "#059669", "bg": "#ECFDF5", "label": "12. Sinif"},
}


def _load_units() -> list[dict]:
    payload = get_unites()
    units_raw = payload if isinstance(payload, list) else []

    units: list[dict] = []
    for item in units_raw:
        grade = int(item.get("grade", 0) or 0)
        if grade not in (9, 10, 11, 12):
            continue

        unit_id = int(item.get("id", 0) or 0)
        if unit_id <= 0:
            continue

        units.append(
            {
                "unit_id": unit_id,
                "grade": grade,
                "number": int(item.get("unit_no", 1) or 1),
                "name": item.get("name", f"Unite {unit_id}"),
                "description": item.get("description") or "Bu unite icin aciklama eklenmedi.",
                "question_count": 0,
            }
        )

    units.sort(key=lambda u: (u["grade"], u["number"]))
    return units


@library_bp.route("/")
@login_required
def index():
    grade_filter = request.args.get("grade", "all")

    all_units = _load_units()

    if grade_filter in ("9", "10", "11", "12"):
        filtered = [u for u in all_units if u["grade"] == int(grade_filter)]
    else:
        grade_filter = "all"
        filtered = all_units

    grouped: dict[int, list[dict]] = {}
    for u in filtered:
        grouped.setdefault(u["grade"], []).append(u)

    grade_counts = {g: len([u for u in all_units if u["grade"] == g]) for g in (9, 10, 11, 12)}

    return render_template(
        "library/index.html",
        units=filtered,
        grouped=grouped,
        grade_filter=grade_filter,
        quiz_types=QUIZ_TYPES,
        grade_meta=GRADE_META,
        total_units=len(all_units),
        grade_counts=grade_counts,
    )

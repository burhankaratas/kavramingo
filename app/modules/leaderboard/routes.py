from flask import render_template, request
from flask_login import login_required, current_user

from app.modules.leaderboard import leaderboard_bp


# Mock leaderboard verisi (backend bağlantısı sonraya bırakıldı)
MOCK_USERS = [
    {"rank": 1,  "name": "Elif Yıldız",       "grade": 9,  "score": 3820, "streak": 21, "accuracy": 94, "you": False},
    {"rank": 2,  "name": "Ahmet Kaya",         "grade": 10, "score": 3650, "streak": 15, "accuracy": 91, "you": False},
    {"rank": 3,  "name": "Zeynep Arslan",      "grade": 11, "score": 3410, "streak": 18, "accuracy": 89, "you": False},
    {"rank": 4,  "name": "Mert Demir",         "grade": 9,  "score": 3280, "streak": 12, "accuracy": 87, "you": False},
    {"rank": 5,  "name": "Selin Çelik",        "grade": 12, "score": 3100, "streak": 9,  "accuracy": 85, "you": False},
    {"rank": 6,  "name": "Burak Şahin",        "grade": 10, "score": 2940, "streak": 7,  "accuracy": 83, "you": False},
    {"rank": 7,  "name": "Ayşe Korkmaz",       "grade": 9,  "score": 2780, "streak": 14, "accuracy": 81, "you": False},
    {"rank": 8,  "name": "Can Yılmaz",         "grade": 11, "score": 2650, "streak": 5,  "accuracy": 80, "you": False},
    {"rank": 9,  "name": "Deniz Aydın",        "grade": 12, "score": 2510, "streak": 3,  "accuracy": 78, "you": False},
    {"rank": 10, "name": "Fatma Öztürk",       "grade": 9,  "score": 2390, "streak": 8,  "accuracy": 77, "you": False},
    {"rank": 11, "name": "Emre Doğan",         "grade": 10, "score": 2250, "streak": 6,  "accuracy": 75, "you": False},
    {"rank": 12, "name": "İrem Karaca",        "grade": 11, "score": 2130, "streak": 4,  "accuracy": 74, "you": False},
    {"rank": 13, "name": "Oğuz Turan",         "grade": 9,  "score": 2010, "streak": 11, "accuracy": 73, "you": False},
    {"rank": 14, "name": "Nisa Aktaş",         "grade": 12, "score": 1890, "streak": 2,  "accuracy": 72, "you": False},
    {"rank": 15, "name": "Sen",                "grade": 9,  "score": 1250, "streak": 7,  "accuracy": 78, "you": True},
]


@leaderboard_bp.route("/")
@login_required
def index():
    grade_filter = request.args.get("grade", "all")

    if grade_filter in ("9", "10", "11", "12"):
        grade_int    = int(grade_filter)
        filtered     = [u for u in MOCK_USERS if u["grade"] == grade_int]
        # rank'ı filtre içinde yeniden hesapla
        for i, u in enumerate(filtered):
            u = dict(u)
            filtered[i] = u
            u["rank"] = i + 1
    else:
        filtered = MOCK_USERS

    # Kullanıcının kendi sırası
    user_entry = next((u for u in filtered if u["you"]), None)

    # Podium: ilk 3
    top3    = filtered[:3]
    rest    = filtered[3:]

    return render_template(
        "leaderboard/index.html",
        entries=filtered,
        top3=top3,
        rest=rest,
        user_entry=user_entry,
        grade_filter=grade_filter,
    )

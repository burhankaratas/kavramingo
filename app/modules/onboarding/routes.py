from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user

from app.clients.kavram_api import get_placement_feed
from app.modules.onboarding import onboarding_bp
from app.extensions import mysql


def _load_questions(grade: int) -> list:
    payload = get_placement_feed(grade)
    items = payload.get("items", []) if isinstance(payload, dict) else []

    questions = []
    for idx, item in enumerate(items, start=1):
        unit = item.get("unit", {})
        q = item.get("question", {})
        choices = q.get("choices", {})
        correct_choice = q.get("correct_choice", "A")
        correct_text = choices.get(correct_choice, "")
        questions.append({
            "id": q.get("id", idx),
            "topic": q.get("topic_name", "Konu"),
            "question": q.get("prompt", ""),
            "choices": [choices.get("A", ""), choices.get("B", ""), choices.get("C", ""), choices.get("D", "")],
            "correct": correct_text,
            "unit_id": unit.get("id"),
            "unit_name": unit.get("name"),
        })
    return questions


# ── Sınıf Seçimi ──────────────────────────────────────────────────────────────
@onboarding_bp.route("/class-select", methods=["GET", "POST"])
@login_required
def class_select():
    # Sınıf zaten seçildiyse dashboard'a yönlendir
    if current_user.grade:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        grade = request.form.get("grade", type=int)
        if grade not in (9, 10, 11, 12):
            flash("Lütfen geçerli bir sınıf seçin.", "danger")
            return render_template("onboarding/class_select.html")

        # Veritabanına yaz
        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET grade = %s WHERE id = %s",
                    (grade, current_user.id))
        mysql.connection.commit()
        cur.close()

        # current_user nesnesini güncelle
        current_user.grade = grade

        # Session'ı temizle (önceki yarım test varsa)
        session.pop("placement_answers", None)
        session.pop("placement_index", None)

        return redirect(url_for("onboarding.placement_test"))

    return render_template("onboarding/class_select.html")


# ── Yerleştirme Testi ─────────────────────────────────────────────────────────
@onboarding_bp.route("/placement-test", methods=["GET", "POST"])
@login_required
def placement_test():
    if not current_user.grade:
        return redirect(url_for("onboarding.class_select"))

    questions = _load_questions(current_user.grade)
    total = len(questions)

    # Session başlat
    if "placement_answers" not in session:
        session["placement_answers"] = []
        session["placement_index"] = 0

    index = session.get("placement_index", 0)

    # Tüm sorular tamamlandıysa sonuç sayfasına git
    if index >= total:
        return redirect(url_for("onboarding.placement_result"))

    current_q = questions[index]

    if request.method == "POST":
        chosen = request.form.get("answer", "").strip()
        is_correct = (chosen == current_q["correct"])

        answers = session.get("placement_answers", [])
        answers.append({
            "id": current_q["id"],
            "topic": current_q["topic"],
            "question": current_q["question"],
            "correct": current_q["correct"],
            "chosen": chosen,
            "is_correct": is_correct,
            "unit_id": current_q.get("unit_id"),
            "unit_name": current_q.get("unit_name"),
        })
        session["placement_answers"] = answers
        session["placement_index"] = index + 1

        # Son soruya cevap verildiyse sonuca git
        if session["placement_index"] >= total:
            return redirect(url_for("onboarding.placement_result"))

        return redirect(url_for("onboarding.placement_test"))

    return render_template(
        "onboarding/placement_test.html",
        question=current_q,
        index=index,
        total=total,
        step=index + 1,
    )


# ── Yerleştirme Sonucu ────────────────────────────────────────────────────────
@onboarding_bp.route("/placement-result")
@login_required
def placement_result():
    if not current_user.grade:
        return redirect(url_for("onboarding.class_select"))

    answers = session.get("placement_answers", [])
    questions = _load_questions(current_user.grade)
    total = len(questions)

    # Testi hiç yapmadıysa teste yönlendir
    if not answers:
        return redirect(url_for("onboarding.placement_test"))

    score = sum(1 for a in answers if a["is_correct"])
    ratio = score / total if total > 0 else 0

    if ratio <= 0.4:
        rec_level = "low"
        rec_text = "Baştan başlamanızı öneririz."
        rec_detail = "Temel konularda eksiklikler tespit edildi. En baştan sağlam bir temel oluşturalım!"
    elif ratio <= 0.8:
        rec_level = "medium"
        # İlk yanlış yapılan konuyu bul
        first_wrong_topic = next(
            (a["topic"] for a in answers if not a["is_correct"]), None
        )
        rec_text = f"'{first_wrong_topic}' konusundan devam etmenizi öneririz." if first_wrong_topic else "Orta seviyeden devam etmenizi öneririz."
        rec_detail = "Bazı konularda bilginiz var ancak bazı noktalarda takviyeye ihtiyaç duyuyor."
    else:
        rec_level = "high"
        rec_text = "İleri seviyeden devam edebilirsiniz."
        rec_detail = "Harika! Temel bilgileriniz çok güçlü. Daha ileri konulara geçebilirsiniz."

    return render_template(
        "onboarding/placement_result.html",
        answers=answers,
        score=score,
        total=total,
        ratio=ratio,
        rec_level=rec_level,
        rec_text=rec_text,
        rec_detail=rec_detail,
    )


# ── Günlük Hedef Seçimi ───────────────────────────────────────────────────────
@onboarding_bp.route("/daily-goal", methods=["GET", "POST"])
@login_required
def daily_goal_select():
    if not current_user.grade:
        return redirect(url_for("onboarding.class_select"))

    # placement_result'tan gelen başlangıç tercihi (beginning / recommended)
    choice = request.args.get("choice", "recommended")

    if request.method == "POST":
        goal   = request.form.get("daily_goal", type=int)
        choice = request.form.get("choice", "recommended")

        if goal not in (3, 5, 10, 15):
            goal = 5  # güvenli fallback

        cur = mysql.connection.cursor()
        cur.execute(
            "UPDATE users SET daily_goal = %s WHERE id = %s",
            (goal, current_user.id)
        )
        mysql.connection.commit()
        cur.close()

        current_user.daily_goal = goal
        return redirect(url_for("onboarding.start", choice=choice))

    return render_template("onboarding/daily_goal.html", choice=choice)


# ── Başlangıç Tercihi ─────────────────────────────────────────────────────────
@onboarding_bp.route("/start")
@login_required
def start():
    choice = request.args.get("choice", "recommended")  # "beginning" veya "recommended"

    # Session'a kaydet, dashboard kullanacak
    session["placement_choice"] = choice

    # Placement session verilerini temizle
    session.pop("placement_answers", None)
    session.pop("placement_index", None)

    return redirect(url_for("dashboard.index"))

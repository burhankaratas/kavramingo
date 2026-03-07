"""
app/modules/quiz/routes.py
──────────────────────────
Quiz modülü route'ları.

Akış:
  /quiz/                        → index: oturum başlatma (GET sorgu parametresi ile)
  /quiz/soru                    → aktif soruyu göster (tip'e göre template seçilir)
  /quiz/cevapla                 → POST: cevabı kaydet, sonraki soruya yönlendir
  /quiz/sonuc                   → oturum tamamlandıktan sonra sonuç ekranı
  /quiz/iptal                   → oturumu iptal et

Sorgu parametreleri (index GET):
  grade     : 9 | 10 | 11 | 12
  unit_id   : 1–16
  quiz_type : multiple_choice | flashcard | matching | fill_blank
"""

import time

from flask import (
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required

from app.extensions import mysql
from app.modules.quiz import quiz_bp
from app.services import quiz_engine
from app.services.badge_service import check_badges
from app.services.scoring import MAX_TIME_PER_QUESTION, format_score_summary

# ── Yardımcı ─────────────────────────────────────────────────────────────────

QUIZ_TYPE_LABELS = {
    "multiple_choice": "Çoktan Seçmeli",
    "flashcard":       "Flashcard",
    "matching":        "Eşleştirme",
    "fill_blank":      "Boşluk Doldurma",
}

QUIZ_TYPE_TEMPLATES = {
    "multiple_choice": "quiz/multiple_choice.html",
    "flashcard":       "quiz/flashcard.html",
    "matching":        "quiz/matching.html",
    "fill_blank":      "quiz/fill_blank.html",
}

VALID_QUIZ_TYPES = set(QUIZ_TYPE_LABELS.keys())
VALID_GRADES     = {9, 10, 11, 12}


# ── Routes ────────────────────────────────────────────────────────────────────

@quiz_bp.route("/")
@login_required
def index():
    """Quiz oturumu başlatır ve ilk soruya yönlendirir."""
    try:
        # grade parametresi yoksa current_user.grade'i kullan
        grade_raw = request.args.get("grade") or getattr(current_user, "grade", None)
        grade     = int(grade_raw) if grade_raw is not None else 0
        unit_id   = int(request.args.get("unit_id", 0))
        quiz_type = request.args.get("quiz_type", "").strip()
    except (ValueError, TypeError):
        flash("Geçersiz quiz parametresi.", "danger")
        return redirect(url_for("dashboard.index"))

    if grade not in VALID_GRADES:
        flash("Sınıf bilgisi eksik veya geçersiz. Lütfen önce onboarding'i tamamlayın.", "danger")
        return redirect(url_for("dashboard.index"))

    if quiz_type not in VALID_QUIZ_TYPES:
        flash("Geçersiz quiz tipi.", "danger")
        return redirect(url_for("dashboard.index"))

    ok = quiz_engine.start_session(grade, unit_id, quiz_type)
    if not ok:
        flash("Bu ünite için soru bulunamadı.", "warning")
        return redirect(url_for("dashboard.index"))

    # Süre takibi için oturum başlangıcını kaydet
    session["q_start"] = time.time()
    session.modified = True

    return redirect(url_for("quiz.question"))


@quiz_bp.route("/soru")
@login_required
def question():
    """Aktif soruyu gösterir."""
    state = quiz_engine.get_session_state()
    if not state:
        return redirect(url_for("dashboard.index"))

    if quiz_engine.is_finished():
        return redirect(url_for("quiz.result"))

    q         = quiz_engine.get_current_question()
    quiz_type = state["quiz_type"]
    template  = QUIZ_TYPE_TEMPLATES.get(quiz_type)
    if not template:
        abort(400)

    current_idx   = state["current"]
    total_q       = len(state["questions"])
    progress_pct  = round(current_idx / total_q * 100)

    # Süre sayacı: her soru için başlat
    session["q_start"] = time.time()
    session.modified = True

    return render_template(
        template,
        question      = q,
        current_index = current_idx + 1,   # 1-tabanlı gösterim
        total         = total_q,
        progress_pct  = progress_pct,
        quiz_type     = quiz_type,
        quiz_type_label = QUIZ_TYPE_LABELS[quiz_type],
        unit_name     = state["unit_name"],
        max_time      = MAX_TIME_PER_QUESTION,
    )


@quiz_bp.route("/cevapla", methods=["POST"])
@login_required
def answer():
    """Cevabı kaydeder, sonraki soruya veya sonuç sayfasına yönlendirir."""
    state = quiz_engine.get_session_state()
    if not state:
        return redirect(url_for("dashboard.index"))

    q         = quiz_engine.get_current_question()
    quiz_type = state["quiz_type"]

    if q is None:
        return redirect(url_for("quiz.result"))

    # ── Süre hesapla ─────────────────────────────────────────────────────────
    q_start   = session.pop("q_start", None)
    time_taken = round(time.time() - q_start, 2) if q_start else None

    # ── Cevap doğruluğunu tip'e göre kontrol et ──────────────────────────────
    given      = ""
    is_correct = False

    if quiz_type == "multiple_choice":
        try:
            chosen_idx = int(request.form.get("choice", -1))
        except ValueError:
            chosen_idx = -1
        given      = str(chosen_idx)
        is_correct = (chosen_idx == q.get("correct_index", -1))

    elif quiz_type == "flashcard":
        # Flashcard: kullanıcı "Biliyorum" / "Bilmiyorum" tıklar
        verdict    = request.form.get("verdict", "no")
        given      = verdict
        is_correct = (verdict == "yes")

    elif quiz_type == "matching":
        # Eşleştirme: form'da pairs[left_idx] = right_text şeklinde gelir
        pairs      = q.get("pairs", [])
        correct    = 0
        given_map  = {}
        for i, pair in enumerate(pairs):
            val = request.form.get(f"match_{i}", "").strip()
            given_map[i] = val
            if val == pair.get("right", ""):
                correct += 1
        given      = str(given_map)
        is_correct = (correct == len(pairs))

    elif quiz_type == "fill_blank":
        given_raw  = (request.form.get("answer", "") or "").strip().lower()
        given      = given_raw
        is_correct = given_raw == q.get("answer", "").strip().lower()

    quiz_engine.record_answer(given, is_correct, time_taken)

    if quiz_engine.is_finished():
        return redirect(url_for("quiz.result"))

    # Süre sayacını bir sonraki soru için başlat
    session["q_start"] = time.time()
    session.modified = True

    return redirect(url_for("quiz.question"))


@quiz_bp.route("/sonuc")
@login_required
def result():
    """
    Quiz sonucunu gösterir.
    finish_session() henüz çağrılmadıysa çağırır (DB'ye yazar).
    """
    # Eğer oturum hâlâ aktifse sonlandır
    state = quiz_engine.get_session_state()
    if state:
        if not quiz_engine.is_finished():
            # Kullanıcı direkt URL'e gitti — tamamlanmamış oturum, iptal et
            quiz_engine.abort_session()
            flash("Quiz yarıda kesildi.", "warning")
            return redirect(url_for("dashboard.index"))

        result_data = quiz_engine.finish_session(current_user.id, mysql)

        # Yeni rozetleri kontrol et
        new_badges = []
        try:
            new_badges = check_badges(current_user.id, mysql)
        except Exception:
            pass  # rozet hatası quiz'i engellemez

        session["quiz_result"]     = result_data
        session["quiz_new_badges"] = [b["name"] for b in new_badges]
        session.modified = True

        return redirect(url_for("quiz.result"))

    # Oturum bitti — sonuç session'dan oku
    result_data = session.pop("quiz_result", None)
    new_badges  = session.pop("quiz_new_badges", [])

    if not result_data:
        return redirect(url_for("dashboard.index"))

    summary = format_score_summary(result_data)

    return render_template(
        "quiz/result.html",
        result     = result_data,
        summary    = summary,
        new_badges = new_badges,
        quiz_type_label = QUIZ_TYPE_LABELS.get(result_data.get("quiz_type", ""), "Quiz"),
    )


@quiz_bp.route("/iptal")
@login_required
def cancel():
    """Aktif quiz oturumunu iptal eder."""
    quiz_engine.abort_session()
    session.pop("q_start", None)
    flash("Quiz iptal edildi.", "info")
    return redirect(url_for("dashboard.index"))

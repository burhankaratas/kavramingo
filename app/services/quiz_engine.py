"""
app/services/quiz_engine.py
───────────────────────────
Quiz oturumu yönetimi: JSON'dan soru yükleme, Flask session aracılığıyla
durum takibi ve DB'ye kayıt.

Tasarım ilkeleri:
  - Her quiz oturumunun durumu Flask session['quiz'] dict içinde tutulur.
  - Oturum tamamlandığında quiz_sessions / quiz_answers / scores tablolarına yazılır.
  - flask_mysqldb + DictCursor kullanılır; ORM yoktur.
  - Soru ID formatı: {sınıf}_{ünite_id}_{tip_kısaltması}_{sıra}  (örn: 9_1_mc_1)
"""

from __future__ import annotations

import json
import os
import random
from datetime import datetime

from flask import session

from app.services.scoring import calculate_quiz_score

# ── Sabitler ─────────────────────────────────────────────────────────────────

QUIZ_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "quiz")
"""JSON soru dosyalarının bulunduğu klasör."""

QUESTIONS_PER_SESSION = 5
"""Bir oturumda sorulacak soru sayısı."""

SESSION_KEY = "quiz"
"""Flask session içindeki anahtar adı."""


# ── Yardımcı ─────────────────────────────────────────────────────────────────

def _grade_file(grade: int) -> str:
    return os.path.join(QUIZ_DATA_DIR, f"grade_{grade}.json")


def _load_grade_data(grade: int) -> dict:
    path = _grade_file(grade)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _get_unit(grade: int, unit_id: int) -> dict | None:
    data = _load_grade_data(grade)
    for unit in data.get("units", []):
        if unit["unit_id"] == unit_id:
            return unit
    return None


# ── Public API ───────────────────────────────────────────────────────────────

def start_session(grade: int, unit_id: int, quiz_type: str) -> bool:
    """
    Yeni bir quiz oturumu başlatır; soruları seçer ve Flask session'a yazar.

    Parametreler
    ------------
    grade     : 9 | 10 | 11 | 12
    unit_id   : JSON'daki unit_id değeri
    quiz_type : 'multiple_choice' | 'flashcard' | 'matching' | 'fill_blank'

    Dönüş
    -----
    True  → oturum başlatıldı
    False → ünite veya o tipteki soru bulunamadı
    """
    unit = _get_unit(grade, unit_id)
    if not unit:
        return False

    all_qs = [q for q in unit.get("questions", []) if q["type"] == quiz_type]
    if not all_qs:
        return False

    chosen = random.sample(all_qs, min(QUESTIONS_PER_SESSION, len(all_qs)))

    session[SESSION_KEY] = {
        "grade":      grade,
        "unit_id":    unit_id,
        "unit_name":  unit.get("name", ""),
        "quiz_type":  quiz_type,
        "questions":  chosen,
        "current":    0,          # mevcut soru indeksi
        "answers":    [],         # [{"question_id", "given", "is_correct", "time"}]
        "started_at": datetime.utcnow().isoformat(),
        "db_session_id": None,    # quiz_sessions.id — DB'ye kaydedilince dolar
    }
    session.modified = True
    return True


def get_current_question() -> dict | None:
    """
    Oturumdaki mevcut soruyu döndürür.
    Oturum yoksa veya sorular bitmişse None döner.
    """
    state = session.get(SESSION_KEY)
    if not state:
        return None
    idx = state["current"]
    qs  = state["questions"]
    if idx >= len(qs):
        return None
    return qs[idx]


def get_session_state() -> dict | None:
    """Tüm oturum bilgisini döndürür (salt okunur kopya)."""
    return session.get(SESSION_KEY)


def record_answer(given_answer: str, is_correct: bool, time_taken: float | None = None) -> None:
    """
    Mevcut sorunun cevabını kaydeder ve bir sonraki soruya geçer.

    Parametreler
    ------------
    given_answer : Kullanıcının verdiği cevap (metin)
    is_correct   : Doğru mu?
    time_taken   : Soruya harcanan süre saniye cinsinden (None → süre bonusu yok)
    """
    state = session.get(SESSION_KEY)
    if not state:
        return

    question = state["questions"][state["current"]]
    state["answers"].append({
        "question_id": question["id"],
        "given":       given_answer,
        "is_correct":  is_correct,
        "time":        time_taken,
    })
    state["current"] += 1
    session.modified = True


def is_finished() -> bool:
    """Tüm sorular cevaplandıysa True döner."""
    state = session.get(SESSION_KEY)
    if not state:
        return True
    return state["current"] >= len(state["questions"])


def calculate_result() -> dict:
    """
    Oturumu puanlar ve sonuç dict döndürür.
    scoring.calculate_quiz_score ile uyumlu.

    Dönüş (scoring.calculate_quiz_score çıktısına ek olarak):
        unit_name  (str)
        quiz_type  (str)
        total_q    (int)
        answers    (list) — kaydedilen her cevabın detayı
    """
    state = session.get(SESSION_KEY)
    if not state:
        return {}

    answers   = state["answers"]
    booleans  = [a["is_correct"] for a in answers]
    times     = [a["time"] for a in answers]

    # Tüm süreler None ise scoring'e None geçir
    if all(t is None for t in times):
        times = None

    result = calculate_quiz_score(booleans, state["quiz_type"], times)
    result.update({
        "unit_name": state["unit_name"],
        "quiz_type": state["quiz_type"],
        "total_q":   len(state["questions"]),
        "answers":   answers,
    })
    return result


def finish_session(user_id: int, mysql) -> dict:
    """
    Oturumu sonlandırır:
      1. Puanı hesaplar.
      2. quiz_sessions.finished_at günceller (veya INSERT yapar).
      3. quiz_answers satırlarını ekler.
      4. scores tablosuna yazar.
      5. users.total_score arttırır.
      6. Flask session'dan quiz verisini temizler.

    Dönüş: calculate_result() çıktısı (DB'ye yazılmadan önce hesaplanır).
    """
    state = session.get(SESSION_KEY)
    if not state:
        return {}

    result = calculate_result()
    now    = datetime.utcnow()

    cur = mysql.connection.cursor()

    try:
        # ── quiz_sessions kaydı ─────────────────────────────────────────────
        db_sid = state.get("db_session_id")
        if db_sid:
            cur.execute(
                "UPDATE quiz_sessions SET finished_at=%s WHERE id=%s",
                (now, db_sid),
            )
        else:
            cur.execute(
                """INSERT INTO quiz_sessions
                   (user_id, unite_id, quiz_type, started_at, finished_at)
                   VALUES (%s, %s, %s, %s, %s)""",
                (
                    user_id,
                    state["unit_id"],
                    state["quiz_type"],
                    state["started_at"],
                    now,
                ),
            )
            db_sid = cur.lastrowid

        # ── quiz_answers satırları ───────────────────────────────────────────
        for ans in state["answers"]:
            # kavram_id: soru ID'sinin son parçasını (sıra no) sayısal olarak al
            try:
                kavram_id = int(ans["question_id"].split("_")[-1])
            except (ValueError, AttributeError):
                kavram_id = 0

            cur.execute(
                """INSERT INTO quiz_answers
                   (session_id, kavram_id, given_answer, is_correct)
                   VALUES (%s, %s, %s, %s)""",
                (db_sid, kavram_id, ans["given"], int(ans["is_correct"])),
            )

        # ── scores tablosu ───────────────────────────────────────────────────
        if result.get("total_score", 0) > 0:
            cur.execute(
                """INSERT INTO scores (user_id, points, source_quiz_id, earned_at)
                   VALUES (%s, %s, %s, %s)""",
                (user_id, result["total_score"], db_sid, now),
            )

        # ── users.total_score ────────────────────────────────────────────────
        cur.execute(
            "UPDATE users SET total_score = total_score + %s WHERE id = %s",
            (result["total_score"], user_id),
        )

        # ── progress tablosu upsert ──────────────────────────────────────────
        # Bu ünite için toplam tamamlanan oturum sayısını hesapla
        cur.execute(
            """SELECT COUNT(*) AS cnt FROM quiz_sessions
               WHERE user_id = %s AND unite_id = %s AND finished_at IS NOT NULL""",
            (user_id, state["unit_id"]),
        )
        unit_sessions = (cur.fetchone() or {}).get("cnt", 0)

        from app.modules.progress.routes import UNIT_QUIZ_TARGET  # yerel import — döngüsel bağımlılığı önler
        if unit_sessions >= UNIT_QUIZ_TARGET:
            new_status = "completed"
        else:
            new_status = "in_progress"

        cur.execute(
            """INSERT INTO progress (user_id, unite_id, status, updated_at)
               VALUES (%s, %s, %s, %s)
               ON DUPLICATE KEY UPDATE status = VALUES(status), updated_at = VALUES(updated_at)""",
            (user_id, state["unit_id"], new_status, now),
        )

        mysql.connection.commit()

    except Exception:
        mysql.connection.rollback()
        raise

    finally:
        cur.close()

    # Session temizle
    session.pop(SESSION_KEY, None)

    result["db_session_id"] = db_sid
    return result


def abort_session() -> None:
    """Yarım kalan oturumu temizler (kullanıcı çıktıysa / yönlendirildiyse)."""
    session.pop(SESSION_KEY, None)

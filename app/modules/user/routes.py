import json
import os
from datetime import datetime, timedelta

from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, login_user, logout_user, current_user
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from werkzeug.security import generate_password_hash, check_password_hash

from app.modules.user import user_bp
from app.extensions import mysql, mail
from app.models.user import User
from app.services.badge_service import get_user_streak


# ── Ayarlar: token yardımcıları ───────────────────────────────────────────────

def _make_delete_token(user_id: int) -> str:
    """Hesap silme için imzalı, 1 saatlik token üretir."""
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return s.dumps(user_id, salt="account-delete")


def _verify_delete_token(token: str, max_age: int = 3600):
    """Token'ı doğrular; geçersizse None döner."""
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        return s.loads(token, salt="account-delete", max_age=max_age)
    except (SignatureExpired, BadSignature):
        return None

# Kategori meta verisi — sıralı
CATEGORY_ORDER = ["baslangic", "seri", "quiz", "mukemmellik", "unite"]

CATEGORY_META = {
    "baslangic":   {"label": "Başlangıç",   "icon": "bi-rocket-takeoff-fill", "color": "#4361EE"},
    "seri":        {"label": "Seri",         "icon": "bi-fire",                "color": "#D9730D"},
    "quiz":        {"label": "Quiz Ustası",  "icon": "bi-mortarboard-fill",    "color": "#7209B7"},
    "mukemmellik": {"label": "Mükemmellik",  "icon": "bi-gem",                 "color": "#059669"},
    "unite":       {"label": "Ünite",        "icon": "bi-collection-fill",     "color": "#0099B8"},
}

# Quiz tipi → (template type, Türkçe başlık)
_QUIZ_TYPE_MAP = {
    "multiple_choice": ("quiz",  "Çoktan Seçmeli Quiz"),
    "flashcard":       ("flash", "Flashcard Çalışması"),
    "matching":        ("match", "Eşleştirme Oyunu"),
    "fill_blank":      ("fill",  "Boşluk Doldurma"),
}


# ── Yardımcılar ───────────────────────────────────────────────────────────────

def _load_unit_map() -> dict:
    """Tüm grade JSON'larından {unit_id: (unit_name, grade)} sözlüğü döndürür."""
    base = os.path.join(os.path.dirname(__file__), "..", "..", "data", "quiz")
    unit_map = {}
    for grade in [9, 10, 11, 12]:
        path = os.path.join(base, f"grade_{grade}.json")
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            for u in data.get("units", []):
                unit_map[u["unit_id"]] = (u.get("name", f"Ünite {u['unit_id']}"), grade)
        except (FileNotFoundError, KeyError):
            pass
    return unit_map


def _time_ago(dt: datetime) -> str:
    """datetime → '2 saat önce' biçiminde Türkçe göreli zaman."""
    if dt is None:
        return ""
    now = datetime.utcnow()
    diff = now - dt
    minutes = int(diff.total_seconds() // 60)
    if minutes < 2:
        return "Az önce"
    if minutes < 60:
        return f"{minutes} dakika önce"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} saat önce"
    days = hours // 24
    if days == 1:
        return "Dün"
    if days < 7:
        return f"{days} gün önce"
    weeks = days // 7
    if weeks == 1:
        return "1 hafta önce"
    return f"{weeks} hafta önce"


# ── Route: Profil ─────────────────────────────────────────────────────────────

@user_bp.route("/profile")
@login_required
def profile():
    uid   = current_user.id
    grade = current_user.grade or 9
    cur   = mysql.connection.cursor()

    # ── 1. Streak ────────────────────────────────────────────────────────────
    cur.execute("SELECT streak FROM users WHERE id = %s", (uid,))
    row    = cur.fetchone()
    streak = row["streak"] if row else 0

    # ── 2. Temel istatistikler ────────────────────────────────────────────────
    cur.execute("""
        SELECT COUNT(*) AS cnt
        FROM quiz_sessions
        WHERE user_id = %s AND finished_at IS NOT NULL
    """, (uid,))
    total_quizzes = cur.fetchone()["cnt"]

    cur.execute("""
        SELECT COALESCE(ROUND(
            SUM(qa.is_correct) * 100.0 / NULLIF(COUNT(qa.id), 0)
        ), 0) AS acc
        FROM quiz_answers qa
        JOIN quiz_sessions qs ON qs.id = qa.session_id
        WHERE qs.user_id = %s AND qs.finished_at IS NOT NULL
    """, (uid,))
    accuracy = int(cur.fetchone()["acc"] or 0)

    # Sınıf içi sıralama (aynı grade'deki kullanıcılar arasında)
    cur.execute("""
        SELECT COUNT(*) + 1 AS rnk
        FROM users
        WHERE total_score > %s AND grade = %s
    """, (current_user.total_score or 0, grade))
    rank = cur.fetchone()["rnk"]

    cur.execute("""
        SELECT COUNT(*) AS cnt FROM user_badges WHERE user_id = %s
    """, (uid,))
    earned_badge_count = cur.fetchone()["cnt"]

    # ── 3. Bu haftanın istatistikleri ─────────────────────────────────────────
    week_ago = datetime.utcnow() - timedelta(days=7)

    cur.execute("""
        SELECT COUNT(*) AS cnt
        FROM quiz_sessions
        WHERE user_id = %s AND finished_at IS NOT NULL AND finished_at >= %s
    """, (uid, week_ago))
    weekly_quizzes = cur.fetchone()["cnt"]

    cur.execute("""
        SELECT COALESCE(SUM(points), 0) AS xp
        FROM scores
        WHERE user_id = %s AND earned_at >= %s
    """, (uid, week_ago))
    weekly_xp = int(cur.fetchone()["xp"] or 0)

    cur.execute("""
        SELECT COALESCE(ROUND(
            SUM(qa.is_correct) * 100.0 / NULLIF(COUNT(qa.id), 0)
        ), 0) AS acc
        FROM quiz_answers qa
        JOIN quiz_sessions qs ON qs.id = qa.session_id
        WHERE qs.user_id = %s AND qs.finished_at IS NOT NULL AND qs.finished_at >= %s
    """, (uid, week_ago))
    weekly_accuracy = int(cur.fetchone()["acc"] or 0)

    cur.execute("""
        SELECT COALESCE(SUM(TIMESTAMPDIFF(MINUTE, started_at, finished_at)), 0) AS mins
        FROM quiz_sessions
        WHERE user_id = %s AND finished_at IS NOT NULL AND finished_at >= %s
    """, (uid, week_ago))
    weekly_minutes = int(cur.fetchone()["mins"] or 0)

    # ── 4. Kazanılan rozetler ─────────────────────────────────────────────────
    cur.execute("""
        SELECT b.emoji, b.name, b.color, b.category, ub.earned_at
        FROM user_badges ub
        JOIN badges b ON b.id = ub.badge_id
        WHERE ub.user_id = %s
        ORDER BY ub.earned_at DESC
    """, (uid,))
    badges = []
    for r in cur.fetchall():
        cat   = r.get("category", "")
        style = {"seri": "blue", "quiz": "purple", "unite": "green"}.get(cat, "")
        badges.append({
            "icon":   r["emoji"] or "🏅",
            "name":   r["name"],
            "earned": True,
            "style":  style,
            "date":   f"{r['earned_at'].day} {r['earned_at'].strftime('%B %Y')}" if r["earned_at"] else "",
        })

    # ── 5. Son aktiviteler ────────────────────────────────────────────────────
    cur.execute("""
        SELECT qs.id, qs.unite_id, qs.quiz_type, qs.finished_at,
               COALESCE(sc.points, 0) AS xp
        FROM quiz_sessions qs
        LEFT JOIN scores sc ON sc.source_quiz_id = qs.id
        WHERE qs.user_id = %s AND qs.finished_at IS NOT NULL
        ORDER BY qs.finished_at DESC
        LIMIT 5
    """, (uid,))
    unit_map = _load_unit_map()
    recent_activities = []
    for r in cur.fetchall():
        qtype, qtitle = _QUIZ_TYPE_MAP.get(r["quiz_type"], ("quiz", r["quiz_type"]))
        unit_id = r["unite_id"]
        if unit_id and unit_id in unit_map:
            uname, ugrade = unit_map[unit_id]
            sub = f"{uname} — {ugrade}. Sınıf"
        else:
            sub = f"{grade}. Sınıf"
        recent_activities.append({
            "type":  qtype,
            "title": qtitle,
            "sub":   sub,
            "xp":    r["xp"],
            "time":  _time_ago(r["finished_at"]),
        })

    # ── 6. Ünite ilerleme ─────────────────────────────────────────────────────
    base_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "data", "quiz", f"grade_{grade}.json"
    )
    grade_units = []
    try:
        with open(base_path, encoding="utf-8") as f:
            grade_units = json.load(f).get("units", [])
    except (FileNotFoundError, KeyError):
        pass

    unit_progress = []
    if grade_units:
        unit_ids = [u["unit_id"] for u in grade_units]
        fmt = ",".join(["%s"] * len(unit_ids))
        cur.execute(f"""
            SELECT unite_id, COUNT(DISTINCT quiz_type) AS done
            FROM quiz_sessions
            WHERE user_id = %s AND finished_at IS NOT NULL AND unite_id IN ({fmt})
            GROUP BY unite_id
        """, [uid] + unit_ids)
        done_map = {r["unite_id"]: r["done"] for r in cur.fetchall()}
        for u in grade_units:
            done = done_map.get(u["unit_id"], 0)
            unit_progress.append({
                "name": u.get("name", f"Ünite {u['unit_id']}"),
                "pct":  min(100, int(done / 4 * 100)),
            })

    cur.close()

    return render_template(
        "user/profile.html",
        streak             = streak,
        total_quizzes      = total_quizzes,
        accuracy           = accuracy,
        rank               = rank,
        earned_badge_count = earned_badge_count,
        badges             = badges,
        recent_activities  = recent_activities,
        unit_progress      = unit_progress,
        weekly_quizzes     = weekly_quizzes,
        weekly_xp          = weekly_xp,
        weekly_accuracy    = weekly_accuracy,
        weekly_minutes     = weekly_minutes,
    )


@user_bp.route("/settings")
@login_required
def settings():
    return render_template("user/settings.html")


# ── Ayarlar: Profil güncelleme ────────────────────────────────────────────────

@user_bp.route("/settings/profile", methods=["POST"])
@login_required
def settings_profile():
    name       = request.form.get("full_name", "").strip()
    grade      = request.form.get("grade", "").strip()
    daily_goal = request.form.get("daily_goal", "").strip()

    if not name:
        flash("Ad soyad boş bırakılamaz.", "danger")
        return redirect(url_for("user.settings"))

    if grade not in {"9", "10", "11", "12"}:
        flash("Geçersiz sınıf değeri.", "danger")
        return redirect(url_for("user.settings"))

    if daily_goal not in {"3", "5", "10", "15"}:
        flash("Geçersiz günlük hedef değeri.", "danger")
        return redirect(url_for("user.settings"))

    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE users SET name = %s, grade = %s, daily_goal = %s WHERE id = %s",
        (name, int(grade), int(daily_goal), current_user.id),
    )
    mysql.connection.commit()
    cur.close()

    flash("Bilgiler başarıyla güncellendi.", "success")
    return redirect(url_for("user.settings"))


# ── Ayarlar: Şifre değiştirme ─────────────────────────────────────────────────

@user_bp.route("/settings/password", methods=["POST"])
@login_required
def settings_password():
    current_pw  = request.form.get("current_password", "")
    new_pw      = request.form.get("new_password", "")
    confirm_pw  = request.form.get("confirm_password", "")

    if not check_password_hash(current_user.password_hash, current_pw):
        flash("Mevcut şifre hatalı.", "danger")
        return redirect(url_for("user.settings"))

    if len(new_pw) < 8:
        flash("Yeni şifre en az 8 karakter olmalıdır.", "danger")
        return redirect(url_for("user.settings"))

    if new_pw != confirm_pw:
        flash("Yeni şifreler eşleşmiyor.", "danger")
        return redirect(url_for("user.settings"))

    new_hash = generate_password_hash(new_pw)
    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE users SET password_hash = %s WHERE id = %s",
        (new_hash, current_user.id),
    )
    mysql.connection.commit()
    cur.close()

    flash("Şifren başarıyla güncellendi.", "success")
    return redirect(url_for("user.settings"))


# ── Ayarlar: Hesap silme isteği (mail gönder) ─────────────────────────────────

@user_bp.route("/settings/delete/request", methods=["POST"])
@login_required
def settings_delete_request():
    token       = _make_delete_token(current_user.id)
    confirm_url = url_for("user.settings_delete_confirm", token=token, _external=True)

    try:
        msg = Message(
            subject="KavramLingo — Hesap Silme Onayı",
            recipients=[current_user.email],
        )
        msg.html = f"""
        <div style="font-family:'Nunito',Arial,sans-serif;max-width:520px;margin:auto;
                    background:#F0F2FF;border-radius:20px;padding:2.5rem;">
          <h2 style="color:#4361EE;margin-top:0;">Hesap Silme İsteği</h2>
          <p style="color:#1B1F3B;font-size:1rem;line-height:1.6;">
            KavramLingo hesabını kalıcı olarak silmek istediğine dair bir istek aldık.<br>
            Eğer bu isteği sen gönderdiysen, aşağıdaki düğmeye tıkla.
          </p>
          <p style="text-align:center;margin:2rem 0;">
            <a href="{confirm_url}"
               style="background:#EF233C;color:#fff;padding:14px 30px;border-radius:12px;
                      text-decoration:none;font-weight:800;font-size:1rem;">
              Hesabımı Kalıcı Olarak Sil
            </a>
          </p>
          <p style="color:#6B7280;font-size:0.85rem;line-height:1.55;">
            Bu bağlantı <strong>1 saat</strong> geçerlidir.<br>
            Eğer bu isteği sen göndermediysen bu e-postayı yoksay — hesabın güvende.
          </p>
          <hr style="border:none;border-top:1px solid #D1D5DB;margin:1.5rem 0;">
          <p style="color:#9CA3AF;font-size:0.78rem;margin:0;">
            KavramLingo &middot; Din Kültürü &amp; Ahlak Bilgisi Öğrenme Platformu
          </p>
        </div>
        """
        mail.send(msg)
        flash(
            "Silme onay bağlantısı e-posta adresine gönderildi. "
            "Bağlantı 1 saat geçerlidir.",
            "warning",
        )
    except Exception:
        flash("Mail gönderilemedi. Lütfen daha sonra tekrar dene.", "danger")

    return redirect(url_for("user.settings"))


# ── Ayarlar: Hesap silme onayı (token doğrula + sil) ─────────────────────────

@user_bp.route("/settings/delete/confirm/<token>")
@login_required
def settings_delete_confirm(token):
    user_id = _verify_delete_token(token)

    if user_id is None:
        flash("Bağlantı geçersiz veya süresi dolmuş.", "danger")
        return redirect(url_for("user.settings"))

    if int(user_id) != int(current_user.id):
        flash("Bu bağlantı sana ait değil.", "danger")
        return redirect(url_for("user.settings"))

    uid = int(user_id)
    cur = mysql.connection.cursor()

    # Bağlı verileri CASCADE sıraya göre sil
    cur.execute("""
        DELETE qa FROM quiz_answers qa
        JOIN quiz_sessions qs ON qs.id = qa.session_id
        WHERE qs.user_id = %s
    """, (uid,))
    cur.execute("DELETE FROM quiz_sessions WHERE user_id = %s", (uid,))
    cur.execute("DELETE FROM scores WHERE user_id = %s", (uid,))
    cur.execute("DELETE FROM user_badges WHERE user_id = %s", (uid,))
    cur.execute("DELETE FROM progress WHERE user_id = %s", (uid,))
    cur.execute("DELETE FROM users WHERE id = %s", (uid,))
    mysql.connection.commit()
    cur.close()

    logout_user()
    flash("Hesabın kalıcı olarak silindi.", "info")
    return redirect(url_for("auth.login"))


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

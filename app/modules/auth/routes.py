import os
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask_mail import Message

from app.modules.auth import auth_bp
from app.modules.auth.forms import RegisterForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
from app.extensions import mysql, mail
from app.models.user import User


def _recaptcha_ok(response_token):
    secret = os.getenv("RECAPTCHA_SECRET_KEY", "")
    if not secret:
        return True
    import requests as req
    try:
        r = req.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={"secret": secret, "response": response_token},
            timeout=5,
        )
        return r.json().get("success", False)
    except Exception:
        return False


def _make_token(email):
    """E-posta için imzalı, 1 saatlik geçerli token üretir."""
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return s.dumps(email, salt="password-reset")


def _verify_token(token, max_age=3600):
    """Token'ı doğrular; geçersizse None döner."""
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        return s.loads(token, salt="password-reset", max_age=max_age)
    except (SignatureExpired, BadSignature):
        return None


# ── Kayıt ──────────────────────────────────────────────────────────────────
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = RegisterForm()

    if form.validate_on_submit():
        token = request.form.get("g-recaptcha-response", "")
        if not _recaptcha_ok(token):
            flash("Robot doğrulaması başarısız. Lütfen tekrar deneyin.", "danger")
            return render_template("auth/register.html", form=form)

        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM users WHERE email = %s", (form.email.data.lower(),))
        if cur.fetchone():
            cur.close()
            flash("Bu e-posta adresi zaten kayıtlı.", "danger")
            return render_template("auth/register.html", form=form)

        cur.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
            (
                form.name.data.strip(),
                form.email.data.lower().strip(),
                generate_password_hash(form.password.data),
            ),
        )
        mysql.connection.commit()
        new_id = cur.lastrowid
        cur.close()

        user = User(id=new_id, name=form.name.data.strip(), email=form.email.data.lower())
        login_user(user, remember=False)

        flash("Hesabınız oluşturuldu! Şimdi sınıfınızı seçelim.", "success")
        return redirect(url_for("onboarding.class_select"))

    return render_template("auth/register.html", form=form)


# ── Giriş ──────────────────────────────────────────────────────────────────
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()

    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (form.email.data.lower(),))
        row = cur.fetchone()
        cur.close()

        if row is None or not check_password_hash(row["password_hash"], form.password.data):
            flash("E-posta veya şifre hatalı.", "danger")
            return render_template("auth/login.html", form=form)

        user = User.from_row(row)
        login_user(user, remember=False)

        next_page = request.args.get("next")
        if next_page:
            return redirect(next_page)
        if not user.grade:
            return redirect(url_for("onboarding.class_select"))
        return redirect(url_for("dashboard.index"))

    return render_template("auth/login.html", form=form)


# ── Çıkış ──────────────────────────────────────────────────────────────────
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Başarıyla çıkış yaptınız.", "info")
    return redirect(url_for("auth.login"))


# ── Şifremi Unuttum ────────────────────────────────────────────────────────
@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = ForgotPasswordForm()

    if form.validate_on_submit():
        token = request.form.get("g-recaptcha-response", "")
        if not _recaptcha_ok(token):
            flash("Robot doğrulaması başarısız. Lütfen tekrar deneyin.", "danger")
            return render_template("auth/forgot_password.html", form=form)

        email = form.email.data.lower().strip()

        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        # Güvenlik: kullanıcı olup olmadığını belli etme
        flash("Eğer bu e-posta kayıtlıysa sıfırlama bağlantısı gönderildi.", "info")

        if user:
            token = _make_token(email)
            reset_url = url_for("auth.reset_password", token=token, _external=True)
            msg = Message(
                subject="KavramLingo — Şifre Sıfırlama",
                recipients=[email],
                html=f"""
                <p>Merhaba,</p>
                <p>Şifreni sıfırlamak için aşağıdaki bağlantıya tıkla.
                   Bu bağlantı <strong>1 saat</strong> geçerlidir.</p>
                <p>
                  <a href="{reset_url}"
                     style="background:#4361EE;color:#fff;padding:10px 20px;
                            border-radius:6px;text-decoration:none;display:inline-block;">
                    Şifremi Sıfırla
                  </a>
                </p>
                <p>Bu isteği sen yapmadıysan bu e-postayı görmezden gelebilirsin.</p>
                <p>— KavramLingo Ekibi</p>
                """,
            )
            mail.send(msg)

        return redirect(url_for("auth.login"))

    return render_template("auth/forgot_password.html", form=form)


# ── Şifre Sıfırlama ────────────────────────────────────────────────────────
@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    email = _verify_token(token)
    if email is None:
        flash("Sıfırlama bağlantısı geçersiz veya süresi dolmuş.", "danger")
        return redirect(url_for("auth.forgot_password"))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        cur.execute(
            "UPDATE users SET password_hash = %s WHERE email = %s",
            (generate_password_hash(form.password.data), email),
        )
        mysql.connection.commit()
        cur.close()

        flash("Şifren başarıyla güncellendi. Giriş yapabilirsin.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", form=form, token=token)

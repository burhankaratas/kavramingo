from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo
)


class RegisterForm(FlaskForm):
    name = StringField(
        "Ad Soyad",
        validators=[
            DataRequired(message="Ad soyad zorunludur."),
            Length(min=2, max=100, message="Ad soyad 2-100 karakter olmalıdır."),
        ],
    )
    email = StringField(
        "E-posta",
        validators=[
            DataRequired(message="E-posta zorunludur."),
            Email(message="Geçerli bir e-posta adresi giriniz."),
            Length(max=150),
        ],
    )
    password = PasswordField(
        "Şifre",
        validators=[
            DataRequired(message="Şifre zorunludur."),
            Length(min=6, max=128, message="Şifre en az 6 karakter olmalıdır."),
        ],
    )
    password2 = PasswordField(
        "Şifre Tekrar",
        validators=[
            DataRequired(message="Şifre tekrarı zorunludur."),
            EqualTo("password", message="Şifreler eşleşmiyor."),
        ],
    )
    submit = SubmitField("Kayıt Ol")


class LoginForm(FlaskForm):
    email = StringField(
        "E-posta",
        validators=[
            DataRequired(message="E-posta zorunludur."),
            Email(message="Geçerli bir e-posta adresi giriniz."),
        ],
    )
    password = PasswordField(
        "Şifre",
        validators=[DataRequired(message="Şifre zorunludur.")],
    )
    submit = SubmitField("Giriş Yap")


class ForgotPasswordForm(FlaskForm):
    email = StringField(
        "E-posta",
        validators=[
            DataRequired(message="E-posta zorunludur."),
            Email(message="Geçerli bir e-posta adresi giriniz."),
        ],
    )
    submit = SubmitField("Sıfırlama Bağlantısı Gönder")


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        "Yeni Şifre",
        validators=[
            DataRequired(message="Şifre zorunludur."),
            Length(min=6, max=128, message="Şifre en az 6 karakter olmalıdır."),
        ],
    )
    password2 = PasswordField(
        "Şifre Tekrar",
        validators=[
            DataRequired(message="Şifre tekrarı zorunludur."),
            EqualTo("password", message="Şifreler eşleşmiyor."),
        ],
    )
    submit = SubmitField("Şifremi Güncelle")

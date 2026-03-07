import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    KAVRAM_API_BASE_URL = os.getenv("KAVRAM_API_BASE_URL", "http://localhost:8000")

    MYSQL_HOST = os.getenv("DB_HOST", "127.0.0.1")
    MYSQL_PORT = int(os.getenv("DB_PORT", "3306"))
    MYSQL_USER = os.getenv("DB_USER", "root")
    MYSQL_PASSWORD = os.getenv("DB_PASSWORD", "")
    MYSQL_DB = os.getenv("DB_NAME", "kavramingo")
    MYSQL_CURSORCLASS = "DictCursor"
    MYSQL_CHARSET = "utf8mb4"
    MYSQL_UNIX_SOCKET = os.getenv("DB_SOCKET", "/opt/lampp/var/mysql/mysql.sock")

    # Google reCAPTCHA v2 — boş bırakılırsa geliştirme modunda doğrulama atlanır
    RECAPTCHA_SITE_KEY   = os.getenv("RECAPTCHA_SITE_KEY", "")
    RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY", "")

    # Flask-Mail — Gmail SMTP
    MAIL_SERVER   = "smtp.gmail.com"
    MAIL_PORT     = 587
    MAIL_USE_TLS  = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = ("KavramLingo", os.getenv("MAIL_USERNAME", ""))


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}

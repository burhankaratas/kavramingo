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
    MYSQL_UNIX_SOCKET = os.getenv("DB_SOCKET", "/opt/lampp/var/mysql/mysql.sock")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}

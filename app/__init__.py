import os
from flask import Flask
from config import config
from app.extensions import mysql, login_manager, mail


def create_app(env=None):
    if env is None:
        env = os.getenv("FLASK_ENV", "default")

    app = Flask(__name__)
    app.config.from_object(config[env])

    # Extensions
    mysql.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Blueprints
    from app.modules.auth import auth_bp
    from app.modules.user import user_bp
    from app.modules.onboarding import onboarding_bp
    from app.modules.quiz import quiz_bp
    from app.modules.dashboard import dashboard_bp
    from app.modules.leaderboard import leaderboard_bp
    from app.modules.library import library_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(onboarding_bp, url_prefix="/onboarding")
    app.register_blueprint(quiz_bp, url_prefix="/quiz")
    app.register_blueprint(dashboard_bp, url_prefix="/")
    app.register_blueprint(leaderboard_bp, url_prefix="/leaderboard")
    app.register_blueprint(library_bp, url_prefix="/kutuphane")

    # Veritabanı tablolarını oluştur (uygulama ilk başladığında)
    with app.app_context():
        from app.db import init_db
        init_db(app)

    return app

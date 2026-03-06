from flask import Blueprint

user_bp = Blueprint("user", __name__)

from app.modules.user import routes  # noqa: F401, E402

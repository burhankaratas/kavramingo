from flask import Blueprint

quiz_bp = Blueprint("quiz", __name__)

from app.modules.quiz import routes  # noqa: F401, E402

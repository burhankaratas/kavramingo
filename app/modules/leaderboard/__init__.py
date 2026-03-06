from flask import Blueprint

leaderboard_bp = Blueprint("leaderboard", __name__)

from app.modules.leaderboard import routes  # noqa: F401, E402

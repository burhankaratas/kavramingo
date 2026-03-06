from flask import Blueprint

dashboard_bp = Blueprint("dashboard", __name__)

from app.modules.dashboard import routes  # noqa: F401, E402

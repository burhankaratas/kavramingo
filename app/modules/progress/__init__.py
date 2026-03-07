from flask import Blueprint

progress_bp = Blueprint("progress", __name__)

from app.modules.progress import routes  # noqa: F401, E402

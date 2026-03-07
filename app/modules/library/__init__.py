from flask import Blueprint

library_bp = Blueprint("library", __name__)

from app.modules.library import routes  # noqa: F401, E402

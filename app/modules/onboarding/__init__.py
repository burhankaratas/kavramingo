from flask import Blueprint

onboarding_bp = Blueprint("onboarding", __name__)

from app.modules.onboarding import routes  # noqa: F401, E402

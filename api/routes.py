# api/routes.py
from flask import Blueprint
from .v1.accounts import accounts_bp

# Create main API blueprint
api_bp = Blueprint("api", __name__)

# Register v1 blueprints
api_bp.register_blueprint(accounts_bp, url_prefix="/v1")

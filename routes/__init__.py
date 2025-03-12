from flask import Blueprint

routes_bp = Blueprint('routes', __name__)

from .alerta_routes import alerta_bp
from .datos_routes import datos_bp
from .profile_routes import profile_bp

# Exportar los Blueprints para que puedan ser registrados en app.py
__all__ = ['alerta_bp', 'datos_bp', 'profile_bp']
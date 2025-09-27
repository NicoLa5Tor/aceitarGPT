from flask import Flask
from flask_cors import CORS
import logging
from config import config

def create_app(config_name='default'):
    """
    Factory function para crear la aplicación Flask
    
    Args:
        config_name: Nombre de la configuración a usar
        
    Returns:
        Instancia de Flask configurada
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Configurar CORS
    CORS(app, origins=["*"])
    
    # Configurar logging
    configure_logging(app)
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Manejo de errores globales
    register_error_handlers(app)
    
    return app

def configure_logging(app):
    """Configura el sistema de logging"""
    if not app.debug and not app.testing:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
        app.logger.setLevel(logging.INFO)

def register_blueprints(app):
    """Registra todos los blueprints de la aplicación"""
    from app.routes.advisor import advisor_bp
    app.register_blueprint(advisor_bp, url_prefix='/api/v1')

def register_error_handlers(app):
    """Registra manejadores de errores globales"""
    from app.utils.error_handlers import register_error_handlers as reg_handlers
    reg_handlers(app)
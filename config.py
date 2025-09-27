import os
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

class Config:
    """Configuración base de la aplicación"""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_URL = "https://api.openai.com/v1/chat/completions"
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL') or "gpt-3.5-turbo"
    OPENAI_TEMPERATURE = float(os.environ.get('OPENAI_TEMPERATURE', 0.2))
    OPENAI_TIMEOUT = int(os.environ.get('OPENAI_TIMEOUT', 30))
    OPENAI_MAX_TOKENS = int(os.environ.get('OPENAI_MAX_TOKENS', 1000))
    
    # Información de la app
    APP_NAME = os.environ.get('APP_NAME', 'Yamaha Advisor API')
    APP_VERSION = os.environ.get('APP_VERSION', '1.0.0')

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Configuración para testing"""
    DEBUG = True
    TESTING = True
    OPENAI_API_KEY = "test-key"

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
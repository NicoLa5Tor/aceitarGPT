
import os
import sys
from app import create_app

def main():
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    if config_name not in ['development', 'production', 'testing']:
        print(f"Error: Configuración '{config_name}' no válida")
        print("Configuraciones válidas: development, production, testing")
        sys.exit(1)
    
    try:
        app = create_app(config_name)
        
        port = int(os.environ.get('PORT', 5000))
        host = os.environ.get('HOST', '0.0.0.0')
        if not app.config.get('OPENAI_API_KEY'):
            print("⚠️  ADVERTENCIA: OPENAI_API_KEY no configurada")
            print("La aplicación se iniciará pero las solicitudes fallarán")
        print(f"🚀 Iniciando Yamaha Advisor API")
        print(f"   Entorno: {config_name}")
        print(f"   Host: {host}")
        print(f"   Puerto: {port}")
        print(f"   Debug: {app.config['DEBUG']}")
        print(f"   URL: http://{host}:{port}")
        app.run(
            host=host, 
            port=port, 
            debug=app.config['DEBUG'],
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 Aplicación detenida por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error iniciando la aplicación: {str(e)}")
        sys.exit(1)
def create_app_for_wsgi():
    """
    Función para crear la app en entornos WSGI (Gunicorn, uWSGI, etc.)
    
    Returns:
        Flask app instance
    """
    config_name = os.environ.get('FLASK_ENV', 'production')
    return create_app(config_name)
app = create_app_for_wsgi()
if __name__ == '__main__':
    main()
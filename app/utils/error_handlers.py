from flask import jsonify, request, current_app
import logging
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """
    Registra manejadores de errores globales para la aplicación
    
    Args:
        app: Instancia de Flask
    """
    
    @app.errorhandler(400)
    def bad_request(error):
        """Maneja errores 400 - Bad Request"""
        logger.warning(f"Bad request: {request.url} - {str(error)}")
        return jsonify({
            "success": False,
            "error": "Solicitud incorrecta",
            "code": 400,
            "details": str(error.description) if hasattr(error, 'description') else None
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        """Maneja errores 404 - Not Found"""
        logger.warning(f"Endpoint no encontrado: {request.url}")
        return jsonify({
            "success": False,
            "error": "Endpoint no encontrado",
            "code": 404,
            "path": request.path,
            "method": request.method
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Maneja errores 405 - Method Not Allowed"""
        logger.warning(f"Método no permitido: {request.method} {request.url}")
        return jsonify({
            "success": False,
            "error": "Método no permitido",
            "code": 405,
            "method": request.method,
            "path": request.path,
            "allowed_methods": error.valid_methods if hasattr(error, 'valid_methods') else None
        }), 405
    
    @app.errorhandler(415)
    def unsupported_media_type(error):
        """Maneja errores 415 - Unsupported Media Type"""
        logger.warning(f"Tipo de contenido no soportado: {request.content_type}")
        return jsonify({
            "success": False,
            "error": "Tipo de contenido no soportado",
            "code": 415,
            "content_type": request.content_type,
            "expected": "application/json"
        }), 415
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        """Maneja errores 422 - Unprocessable Entity"""
        logger.warning(f"Entidad no procesable: {request.url}")
        return jsonify({
            "success": False,
            "error": "Datos no procesables",
            "code": 422,
            "details": str(error.description) if hasattr(error, 'description') else None
        }), 422
    
    @app.errorhandler(429)
    def too_many_requests(error):
        """Maneja errores 429 - Too Many Requests"""
        logger.warning(f"Demasiadas solicitudes desde: {request.remote_addr}")
        return jsonify({
            "success": False,
            "error": "Demasiadas solicitudes",
            "code": 429,
            "message": "Por favor, inténtalo más tarde"
        }), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        """Maneja errores 500 - Internal Server Error"""
        logger.error(f"Error interno del servidor: {str(error)}", exc_info=True)
        
        # En producción, no revelar detalles del error
        details = None
        if current_app.debug:
            details = str(error)
        
        return jsonify({
            "success": False,
            "error": "Error interno del servidor",
            "code": 500,
            "details": details
        }), 500
    
    @app.errorhandler(502)
    def bad_gateway(error):
        """Maneja errores 502 - Bad Gateway"""
        logger.error(f"Bad gateway: {str(error)}")
        return jsonify({
            "success": False,
            "error": "Error de gateway",
            "code": 502,
            "message": "Servicio temporalmente no disponible"
        }), 502
    
    @app.errorhandler(503)
    def service_unavailable(error):
        """Maneja errores 503 - Service Unavailable"""
        logger.error(f"Servicio no disponible: {str(error)}")
        return jsonify({
            "success": False,
            "error": "Servicio no disponible",
            "code": 503,
            "message": "Por favor, inténtalo más tarde"
        }), 503
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Maneja cualquier otra excepción HTTP"""
        logger.warning(f"Excepción HTTP {error.code}: {request.url}")
        return jsonify({
            "success": False,
            "error": error.name,
            "code": error.code,
            "description": error.description
        }), error.code
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        """Maneja excepciones genéricas no capturadas"""
        logger.error(f"Excepción no manejada: {str(error)}", exc_info=True)
        
        # En producción, no revelar detalles del error
        details = None
        if current_app.debug:
            details = {
                "type": type(error).__name__,
                "message": str(error)
            }
        
        return jsonify({
            "success": False,
            "error": "Error interno del servidor",
            "code": 500,
            "details": details
        }), 500
    
    # Manejar errores de JSON inválido
    @app.errorhandler(400)
    def handle_json_error(error):
        """Maneja errores específicos de JSON malformado"""
        if "Failed to decode JSON object" in str(error):
            logger.warning(f"JSON malformado en solicitud: {request.url}")
            return jsonify({
                "success": False,
                "error": "JSON malformado",
                "code": 400,
                "message": "Verifica que el JSON esté bien formateado"
            }), 400
        
        # Si no es un error de JSON, usar el manejador por defecto
        return bad_request(error)
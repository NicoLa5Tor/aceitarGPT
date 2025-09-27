from flask import Blueprint, request, jsonify, current_app
from marshmallow import ValidationError
from datetime import datetime
import logging

from ..services.openai_service import OpenAIService
from ..models.schemas import ConsultaSchema, RespuestaSchema, ErrorSchema, HealthSchema

advisor_bp = Blueprint('advisor', __name__)
logger = logging.getLogger(__name__)

@advisor_bp.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint de health check
    
    Returns:
        JSON con el estado del servicio
    """
    try:
        health_data = {
            "status": "healthy",
            "service": "Yamaha Advisor API",
            "version": "1.0.0",
            "timestamp": datetime.utcnow()
        }
        
        # Validar respuesta
        schema = HealthSchema()
        validated_response = schema.dump(health_data)
        
        return jsonify(validated_response), 200
        
    except Exception as e:
        logger.error(f"Error en health check: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "service": "Yamaha Advisor API",
            "error": str(e)
        }), 500

@advisor_bp.route('/generar-respuesta', methods=['POST'])
def generar_respuesta():
   
    try:
        # Validar que el request tiene JSON
        if not request.is_json:
            return _create_error_response(
                "Content-Type debe ser application/json", 
                400, 
                {"content_type": request.content_type}
            )
        
        # Validar datos de entrada
        schema = ConsultaSchema()
        data = schema.load(request.json)
        
        # Validar que OpenAI esté configurado
        if not current_app.config.get('OPENAI_API_KEY'):
            return _create_error_response(
                "Servicio no configurado correctamente",
                503,
                {"missing": "OPENAI_API_KEY"}
            )
        
        # Generar respuesta
        openai_service = OpenAIService()
        resultado = openai_service.generate_advisor_response(
            asesor=data['asesor'],
            contexto=data['contexto']
        )
        
        # Validar y serializar respuesta
        response_schema = RespuestaSchema()
        validated_response = response_schema.dump(resultado)
        
        # Log de éxito
        status_code = 200 if resultado['success'] else 422
        logger.info(f"Respuesta generada para asesor: {data['asesor']}, success: {resultado['success']}")
        
        return jsonify(validated_response), status_code
        
    except ValidationError as e:
        logger.warning(f"Error de validación: {e.messages}")
        return _create_error_response(
            "Datos de entrada inválidos",
            400,
            e.messages
        )
        
    except Exception as e:
        logger.error(f"Error interno en generar_respuesta: {str(e)}", exc_info=True)
        return _create_error_response(
            "Error interno del servidor",
            500,
            str(e) if current_app.debug else None
        )

@advisor_bp.route('/ejemplo-contexto', methods=['GET'])
def ejemplo_contexto():
    """
    Endpoint que devuelve ejemplos de contexto válidos
    
    Returns:
        JSON con ejemplos de uso
    """
    ejemplos = {
        "ejemplos": [
            {
                "descripcion": "Consulta por repuestos",
                "asesor": "Andrea Gómez",
                "contexto": "nombre_cliente: 'Juan Pérez', sucursal: 'Yamaha Aceitar 134', repuesto/equipamiento_interes: 'bujías', motivo: 'repuestos_equipamiento', tipo_consulta: 'repuesto'"
            },
            {
                "descripcion": "Consulta por servicio técnico",
                "asesor": "Carlos Rodríguez",
                "contexto": "nombre_cliente: 'María González', sucursal: 'Yamaha Centro', repuesto/equipamiento_interes: 'revisión motor', motivo: 'servicio_tecnico', tipo_consulta: 'mantenimiento'"
            },
            {
                "descripcion": "Consulta general",
                "asesor": "Ana Silva",
                "contexto": "nombre_cliente: 'Cliente', sucursal: 'Yamaha Norte', repuesto/equipamiento_interes: 'información general', motivo: 'consulta_general', tipo_consulta: 'informacion'"
            }
        ],
        "formato_requerido": {
            "asesor": "string (1-100 caracteres)",
            "contexto": "string (1-2000 caracteres)"
        }
    }
    
    return jsonify(ejemplos), 200

@advisor_bp.route('/test-openai', methods=['POST'])
def test_openai():
    """
    Endpoint para probar la conexión con OpenAI (solo en desarrollo)
    
    Returns:
        JSON con el estado de la conexión
    """
    if not current_app.debug:
        return _create_error_response("Endpoint solo disponible en modo debug", 403)
    
    try:
        # Test básico con datos mínimos
        openai_service = OpenAIService()
        resultado = openai_service.generate_advisor_response(
            asesor="Test",
            contexto="nombre_cliente: 'Test', motivo: 'test'"
        )
        
        return jsonify({
            "openai_status": "OK",
            "test_result": resultado
        }), 200
        
    except Exception as e:
        logger.error(f"Error en test OpenAI: {str(e)}")
        return _create_error_response(
            "Error en conexión con OpenAI",
            503,
            str(e)
        )

def _create_error_response(message: str, status_code: int, details=None):
    """
    Crea una respuesta de error estandarizada
    
    Args:
        message: Mensaje de error
        status_code: Código de estado HTTP
        details: Detalles adicionales del error
        
    Returns:
        Tupla (response, status_code)
    """
    error_data = {
        "success": False,
        "error": message,
        "code": status_code,
        "details": details
    }
    
    try:
        error_schema = ErrorSchema()
        validated_error = error_schema.dump(error_data)
        return jsonify(validated_error), status_code
    except Exception:
        # Fallback en caso de error en la validación
        return jsonify({
            "success": False,
            "error": message,
            "code": status_code
        }), status_code
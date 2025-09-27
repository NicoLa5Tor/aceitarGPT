from marshmallow import Schema, fields, validate, ValidationError, post_load
from typing import Dict, Any

class ConsultaSchema(Schema):
 
    asesor = fields.Str(
        required=True, 
        validate=validate.Length(min=1, max=100),
        error_messages={
            'required': 'El campo asesor es requerido',
            'invalid': 'El asesor debe ser una cadena de texto',
            'length': 'El nombre del asesor debe tener entre 1 y 100 caracteres'
        }
    )
    
    contexto = fields.Str(
        required=True, 
        validate=validate.Length(min=1, max=2000),
        error_messages={
            'required': 'El campo contexto es requerido',
            'invalid': 'El contexto debe ser una cadena de texto',
            'length': 'El contexto debe tener entre 1 y 2000 caracteres'
        }
    )
    
    @post_load
    def clean_data(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Limpia y normaliza los datos después de la validación"""
        # Limpiar espacios en blanco
        data['asesor'] = data['asesor'].strip()
        data['contexto'] = data['contexto'].strip()
        
        return data
    
    class Meta:
        strict = True

class RespuestaSchema(Schema):
    """
    Schema para la respuesta del asesor
    
    Campos:
        success: Indica si la operación fue exitosa
        motivo: Motivo de la consulta (opcional)
        mensaje: Mensaje procesado para WhatsApp (opcional)
        mensaje_original: Mensaje original sin procesar (opcional)
        error: Mensaje de error (opcional)
        raw_response: Respuesta cruda en caso de error (opcional)
    """
    success = fields.Bool(
        required=True,
        error_messages={
            'required': 'El campo success es requerido',
            'invalid': 'El campo success debe ser un booleano'
        }
    )
    
    motivo = fields.Str(
        allow_none=True,
        validate=validate.Length(max=200),
        error_messages={
            'invalid': 'El motivo debe ser una cadena de texto',
            'length': 'El motivo no puede exceder 200 caracteres'
        }
    )
    
    mensaje = fields.Str(
        allow_none=True,
        validate=validate.Length(max=1000),
        error_messages={
            'invalid': 'El mensaje debe ser una cadena de texto',
            'length': 'El mensaje no puede exceder 1000 caracteres'
        }
    )
    
    mensaje_original = fields.Str(
        allow_none=True,
        validate=validate.Length(max=1000),
        error_messages={
            'invalid': 'El mensaje original debe ser una cadena de texto',
            'length': 'El mensaje original no puede exceder 1000 caracteres'
        }
    )
    
    error = fields.Str(
        allow_none=True,
        validate=validate.Length(max=500),
        error_messages={
            'invalid': 'El error debe ser una cadena de texto',
            'length': 'El mensaje de error no puede exceder 500 caracteres'
        }
    )
    
    raw_response = fields.Str(
        allow_none=True,
        validate=validate.Length(max=2000),
        error_messages={
            'invalid': 'La respuesta cruda debe ser una cadena de texto',
            'length': 'La respuesta cruda no puede exceder 2000 caracteres'
        }
    )

class ErrorSchema(Schema):
    """Schema para respuestas de error estandarizadas"""
    success = fields.Bool(required=True, default=False)
    error = fields.Str(required=True)
    code = fields.Int(allow_none=True)
    details = fields.Raw(allow_none=True)

class HealthSchema(Schema):
    """Schema para el endpoint de health check"""
    status = fields.Str(required=True)
    service = fields.Str(required=True)
    version = fields.Str(required=True)
    timestamp = fields.DateTime(allow_none=True)
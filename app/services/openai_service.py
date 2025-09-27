import json
import logging
from typing import Any, Dict

import requests

from config import Settings


class OpenAIService:
    """Servicio para manejar interacciones con la API de OpenAI."""

    def __init__(self, settings: Settings):
        self._settings = settings
        self.api_key = settings.openai_api_key
        self.url = settings.openai_url
        self.model = settings.openai_model
        self.temperature = settings.openai_temperature
        self.timeout = settings.openai_timeout
        self.max_tokens = settings.openai_max_tokens
        self.logger = logging.getLogger(__name__)

    def _get_headers(self) -> Dict[str, str]:
        """Obtiene headers para la API de OpenAI."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _create_prompt(self, asesor: str, contexto: str) -> str:
        """Crea el prompt para OpenAI."""
        return f"""Debes responder SOLO con un JSON válido con esta estructura exacta:
{{
  \"motivo\": \"resumen corto del motivo de la consulta\",
  \"mensaje\": \"respuesta del asesor\",
  \"mensaje_original\": \"mensaje formateado para WhatsApp\"
}}

Instrucciones:
- motivo: Resumen fiel usando palabras del cliente
- mensaje: 1) Saludo con nombre del cliente (si es nombre real, corregir ortografía), 2) Presentación con mi nombre como asesor,
 3) Confirmación de TODA la información recibida del cliente (incluir TODO: productos, tallas, especificaciones, condiciones de pago, urgencia, etc.), 4) Pregunta de seguimiento. NO incluir nombre del asesor al final.
- mensaje_original: Mismo mensaje con formato WhatsApp:
  * *texto* solo para nombres propios (cliente y asesor)
  * • para listas de información
  * Doble salto de línea entre secciones
  * NO nombre del asesor al final

IMPORTANTE: Corregir errores ortográficos en nombres (Danela->Daniela) y incluir TODA la información relevante del contexto.

Asesor: {asesor}
Contexto: {contexto}

Responde SOLO el JSON:"""

    def generate_advisor_response(self, asesor: str, contexto: str) -> Dict[str, Any]:
        """Genera respuesta del asesor usando OpenAI."""
        self._validate_config()

        prompt = self._create_prompt(asesor, contexto)
        data = self._prepare_request_data(prompt)

        self.logger.info("Enviando solicitud a OpenAI para asesor: %s", asesor)

        response = self._make_api_request(data)
        mensaje_raw = response["choices"][0]["message"]["content"]

        return self._process_response(mensaje_raw)

    def _validate_config(self) -> None:
        """Valida que la configuración esté completa."""
        if not self.api_key:
            raise ValueError("OpenAI API key no configurada")

    def _prepare_request_data(self, prompt: str) -> Dict[str, Any]:
        """Prepara los datos para la solicitud a OpenAI."""
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "Eres un asesor profesional de Yamaha Aceitar. Solo responde con un JSON válido.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": self.temperature,
        }

        if self.max_tokens:
            payload["max_tokens"] = self.max_tokens

        return payload

    def _make_api_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Realiza la solicitud HTTP a OpenAI."""
        response = requests.post(
            self.url,
            headers=self._get_headers(),
            json=data,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def _process_response(self, mensaje_raw: str) -> Dict[str, Any]:
        """Procesa la respuesta cruda de OpenAI."""
        try:
            json_data = json.loads(mensaje_raw)

            return {
                "success": True,
                "motivo": json_data["motivo"],
                "mensaje": json_data["mensaje"],
                "mensaje_original": json_data["mensaje_original"],
            }
        except json.JSONDecodeError as exc:
            self.logger.warning("Respuesta no es JSON válido: %s", exc)
            self.logger.warning("Respuesta recibida: %s...", mensaje_raw[:500])
            return {
                "success": False,
                "error": f"Respuesta no es JSON válido: {exc}",
                "raw_response": mensaje_raw,
            }

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint_returns_service_status():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["service"]
    assert payload["version"]
    assert "timestamp" in payload


def test_generar_respuesta_without_api_key_returns_503():
    response = client.post(
        "/api/v1/generar-respuesta",
        json={"asesor": "Ana", "contexto": "Consulta de prueba"},
    )
    assert response.status_code == 503
    payload = response.json()
    assert payload["error"] == "Servicio no configurado correctamente"


def test_ejemplo_contexto_returns_examples():
    response = client.get("/api/v1/ejemplo-contexto")
    assert response.status_code == 200
    payload = response.json()
    assert "ejemplos" in payload
    assert isinstance(payload["ejemplos"], list)
    assert payload["ejemplos"], "Se esperaba al menos un ejemplo"

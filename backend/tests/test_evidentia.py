from pathlib import Path

from app.core.config import settings


def _upload(client, case_id, filename="evidence.txt", content=b"contenido de prueba"):
    return client.post(
        f"/api/cases/{case_id}/evidence",
        files={"file": (filename, content, "text/plain")},
        data={"description": "evidencia de test", "source": "pytest"},
    )


def test_upload_evidence(client, sample_case):
    resp = _upload(client, sample_case["id"])
    assert resp.status_code == 201
    data = resp.json()
    assert data["original_filename"] == "evidence.txt"
    assert data["file_size"] == len(b"contenido de prueba")
    assert len(data["sha256"]) == 64  # hex de SHA-256
    assert data["case_id"] == sample_case["id"]


def test_upload_evidence_case_not_found(client):
    resp = _upload(client, 9999)
    assert resp.status_code == 404


def test_list_evidence(client, sample_case):
    _upload(client, sample_case["id"])
    _upload(client, sample_case["id"], filename="otro.txt", content=b"xxx")

    resp = client.get(f"/api/cases/{sample_case['id']}/evidence")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_verify_integrity_ok(client, sample_case):
    ev = _upload(client, sample_case["id"]).json()

    resp = client.post(f"/api/evidence/{ev['id']}/verify")
    assert resp.status_code == 200
    data = resp.json()
    assert data["match"] is True
    assert data["stored_hash"] == data["current_hash"]
    assert "INTEGRIDAD VERIFICADA" in data["message"]


def test_verify_integrity_mismatch(client, sample_case):
    """Manipular el archivo en disco debe hacer fallar la verificación."""
    ev = _upload(client, sample_case["id"]).json()

    storage = Path(settings.STORAGE_PATH)
    file_path = storage / ev["stored_filename"]
    assert file_path.exists(), f"Archivo no encontrado en {file_path}"

    # Sobreescribir con contenido distinto
    file_path.write_bytes(b"contenido manipulado")

    resp = client.post(f"/api/evidence/{ev['id']}/verify")
    assert resp.status_code == 200
    data = resp.json()
    assert data["match"] is False
    assert data["stored_hash"] != data["current_hash"]
    assert "MISMATCH" in data["message"]


def test_verify_evidence_not_found(client):
    resp = client.post("/api/evidence/9999/verify")
    assert resp.status_code == 404


def test_delete_evidence(client, sample_case):
    ev = _upload(client, sample_case["id"]).json()

    resp = client.delete(f"/api/evidence/{ev['id']}")
    assert resp.status_code == 204

    resp = client.get(f"/api/evidence/{ev['id']}")
    assert resp.status_code == 404

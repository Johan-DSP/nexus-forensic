def _payload(**overrides):
    """Payload base de evento, sobreescribible."""
    base = {
        "title": "Evento de prueba",
        "event_type": "OBSERVATION",
        "start_datetime": "2026-01-01T10:00:00Z",
        "end_datetime": "2026-01-01T11:00:00Z",
        "certainty": "CONFIRMED",
    }
    base.update(overrides)
    return base


def test_create_event(client, sample_case):
    resp = client.post(
        f"/api/cases/{sample_case['id']}/events",
        json=_payload(),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["case_id"] == sample_case["id"]
    assert data["event_type"] == "OBSERVATION"
    assert data["title"] == "Evento de prueba"


def test_create_event_invalid_dates(client, sample_case):
    """end_datetime <= start_datetime debe dar 400."""
    resp = client.post(
        f"/api/cases/{sample_case['id']}/events",
        json=_payload(
            start_datetime="2026-01-01T11:00:00Z",
            end_datetime="2026-01-01T10:00:00Z",
        ),
    )
    assert resp.status_code == 400
    assert resp.json()["detail"]["error"] == "INVALID_DATES"


def test_create_event_case_not_found(client):
    resp = client.post("/api/cases/9999/events", json=_payload())
    assert resp.status_code == 404


def test_list_events_sorted_by_start(client, sample_case):
    # Crear en orden inverso
    client.post(
        f"/api/cases/{sample_case['id']}/events",
        json=_payload(
            title="Tarde",
            start_datetime="2026-01-01T15:00:00Z",
            end_datetime="2026-01-01T16:00:00Z",
        ),
    )
    client.post(
        f"/api/cases/{sample_case['id']}/events",
        json=_payload(
            title="Temprano",
            start_datetime="2026-01-01T08:00:00Z",
            end_datetime="2026-01-01T09:00:00Z",
        ),
    )

    resp = client.get(f"/api/cases/{sample_case['id']}/events")
    assert resp.status_code == 200
    titles = [e["title"] for e in resp.json()]
    assert titles == ["Temprano", "Tarde"]


def test_detect_overlaps(client, sample_case):
    """Dos eventos que se solapan 30 minutos."""
    client.post(
        f"/api/cases/{sample_case['id']}/events",
        json=_payload(
            title="A",
            start_datetime="2026-01-01T10:00:00Z",
            end_datetime="2026-01-01T11:00:00Z",
        ),
    )
    client.post(
        f"/api/cases/{sample_case['id']}/events",
        json=_payload(
            title="B",
            start_datetime="2026-01-01T10:30:00Z",
            end_datetime="2026-01-01T11:30:00Z",
        ),
    )

    resp = client.get(f"/api/cases/{sample_case['id']}/events/overlaps")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["overlap_minutes"] == 30.0
    assert data[0]["message"] == "POSIBLE SOLAPAMIENTO TEMPORAL"


def test_no_overlaps(client, sample_case):
    """Eventos disjuntos en el tiempo."""
    client.post(
        f"/api/cases/{sample_case['id']}/events",
        json=_payload(
            start_datetime="2026-01-01T10:00:00Z",
            end_datetime="2026-01-01T11:00:00Z",
        ),
    )
    client.post(
        f"/api/cases/{sample_case['id']}/events",
        json=_payload(
            start_datetime="2026-01-01T12:00:00Z",
            end_datetime="2026-01-01T13:00:00Z",
        ),
    )

    resp = client.get(f"/api/cases/{sample_case['id']}/events/overlaps")
    assert resp.status_code == 200
    assert resp.json() == []


def test_overlaps_ignores_events_without_end(client, sample_case):
    """Los eventos sin end_datetime no cuentan para overlaps."""
    client.post(
        f"/api/cases/{sample_case['id']}/events",
        json=_payload(
            title="Sin fin",
            start_datetime="2026-01-01T10:00:00Z",
            end_datetime=None,
        ),
    )
    client.post(
        f"/api/cases/{sample_case['id']}/events",
        json=_payload(
            title="Con fin",
            start_datetime="2026-01-01T10:30:00Z",
            end_datetime="2026-01-01T11:00:00Z",
        ),
    )

    resp = client.get(f"/api/cases/{sample_case['id']}/events/overlaps")
    assert resp.status_code == 200
    assert resp.json() == []


def test_update_event(client, sample_case):
    ev = client.post(
        f"/api/cases/{sample_case['id']}/events",
        json=_payload(),
    ).json()

    resp = client.put(
        f"/api/events/{ev['id']}",
        json={"title": "Modificado", "certainty": "REPORTED"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Modificado"
    assert data["certainty"] == "REPORTED"


def test_delete_event(client, sample_case):
    ev = client.post(
        f"/api/cases/{sample_case['id']}/events",
        json=_payload(),
    ).json()

    resp = client.delete(f"/api/events/{ev['id']}")
    assert resp.status_code == 204

    resp = client.get(f"/api/events/{ev['id']}")
    assert resp.status_code == 404

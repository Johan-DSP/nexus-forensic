def test_create_case(client):
    resp = client.post(
        "/api/cases/",
        json={
            "case_number": "CASO-001",
            "title": "Investigación inicial",
            "description": "Descripción del caso",
            "status": "OPEN",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["case_number"] == "CASO-001"
    assert data["title"] == "Investigación inicial"
    assert data["status"] == "OPEN"
    assert "id" in data
    assert data["created_at"] is not None


def test_create_case_duplicate_number(client, sample_case):
    resp = client.post(
        "/api/cases/",
        json={
            "case_number": sample_case["case_number"],
            "title": "Otro título",
        },
    )
    assert resp.status_code == 400
    assert resp.json()["detail"]["error"] == "CASE_ALREADY_EXISTS"


def test_list_cases(client, sample_case):
    resp = client.get("/api/cases/")
    assert resp.status_code == 200
    cases = resp.json()
    assert len(cases) == 1
    assert cases[0]["id"] == sample_case["id"]


def test_get_case(client, sample_case):
    resp = client.get(f"/api/cases/{sample_case['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == sample_case["id"]


def test_get_case_not_found(client):
    resp = client.get("/api/cases/9999")
    assert resp.status_code == 404
    assert resp.json()["detail"]["error"] == "CASE_NOT_FOUND"


def test_update_case(client, sample_case):
    resp = client.put(
        f"/api/cases/{sample_case['id']}",
        json={"title": "Título actualizado", "status": "IN_PROGRESS"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Título actualizado"
    assert data["status"] == "IN_PROGRESS"


def test_update_case_partial(client, sample_case):
    resp = client.put(
        f"/api/cases/{sample_case['id']}",
        json={"status": "CLOSED"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "CLOSED"
    assert data["title"] == sample_case["title"]


def test_update_case_not_found(client):
    resp = client.put("/api/cases/9999", json={"title": "X"})
    assert resp.status_code == 404


def test_delete_case(client, sample_case):
    resp = client.delete(f"/api/cases/{sample_case['id']}")
    assert resp.status_code == 204

    resp = client.get(f"/api/cases/{sample_case['id']}")
    assert resp.status_code == 404


def test_delete_case_not_found(client):
    resp = client.delete("/api/cases/9999")
    assert resp.status_code == 404

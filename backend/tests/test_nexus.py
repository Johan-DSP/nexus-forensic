def _create_entity(client, case_id, name="Entidad", entity_type="PERSON", **extra):
    payload = {"type": entity_type, "name": name, **extra}
    return client.post(f"/api/cases/{case_id}/entities", json=payload)


def test_create_entity(client, sample_case):
    resp = _create_entity(client, sample_case["id"], "Alejandro Vargas")
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Alejandro Vargas"
    assert data["type"] == "PERSON"
    assert data["case_id"] == sample_case["id"]
    assert data["metadata"] == {}


def test_create_entity_with_metadata(client, sample_case):
    resp = client.post(
        f"/api/cases/{sample_case['id']}/entities",
        json={
            "type": "VEHICLE",
            "name": "Toyota Hilux",
            "identifier": "ABC-123",
            "metadata": {"color": "negra", "year": 2020},
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["metadata"] == {"color": "negra", "year": 2020}
    assert data["identifier"] == "ABC-123"


def test_list_entities(client, sample_case):
    _create_entity(client, sample_case["id"], "A")
    _create_entity(client, sample_case["id"], "B")

    resp = client.get(f"/api/cases/{sample_case['id']}/entities")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_update_entity(client, sample_case):
    e = _create_entity(client, sample_case["id"]).json()

    resp = client.put(
        f"/api/entities/{e['id']}",
        json={"name": "Modificado", "identifier": "NEW-01"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Modificado"
    assert data["identifier"] == "NEW-01"


def test_create_relationship(client, sample_case):
    e1 = _create_entity(client, sample_case["id"], "A").json()
    e2 = _create_entity(client, sample_case["id"], "B").json()

    resp = client.post(
        f"/api/cases/{sample_case['id']}/relationships",
        json={
            "source_entity_id": e1["id"],
            "target_entity_id": e2["id"],
            "relationship_type": "ASSOCIATED_WITH",
            "confidence": 0.8,
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["source_entity_id"] == e1["id"]
    assert data["target_entity_id"] == e2["id"]
    assert data["relationship_type"] == "ASSOCIATED_WITH"
    assert data["confidence"] == 0.8


def test_self_relationship_rejected(client, sample_case):
    e = _create_entity(client, sample_case["id"], "A").json()

    resp = client.post(
        f"/api/cases/{sample_case['id']}/relationships",
        json={
            "source_entity_id": e["id"],
            "target_entity_id": e["id"],
            "relationship_type": "RELATED_TO",
        },
    )
    assert resp.status_code == 400
    assert resp.json()["detail"]["error"] == "SELF_RELATIONSHIP_NOT_ALLOWED"


def test_cross_case_relationship_rejected(client, sample_case):
    case2 = client.post(
        "/api/cases/",
        json={"case_number": "TEST-002", "title": "Otro caso"},
    ).json()

    e1 = _create_entity(client, sample_case["id"], "A").json()
    e2 = _create_entity(client, case2["id"], "B").json()

    resp = client.post(
        f"/api/cases/{sample_case['id']}/relationships",
        json={
            "source_entity_id": e1["id"],
            "target_entity_id": e2["id"],
            "relationship_type": "RELATED_TO",
        },
    )
    assert resp.status_code == 400
    assert resp.json()["detail"]["error"] == "ENTITY_NOT_IN_CASE"


def test_delete_entity_cascades_relationships(client, sample_case):
    e1 = _create_entity(client, sample_case["id"], "A").json()
    e2 = _create_entity(client, sample_case["id"], "B").json()

    client.post(
        f"/api/cases/{sample_case['id']}/relationships",
        json={
            "source_entity_id": e1["id"],
            "target_entity_id": e2["id"],
            "relationship_type": "RELATED_TO",
        },
    )

    resp = client.delete(f"/api/entities/{e1['id']}")
    assert resp.status_code == 204

    rels = client.get(f"/api/cases/{sample_case['id']}/relationships").json()
    assert rels == []


def test_delete_relationship(client, sample_case):
    e1 = _create_entity(client, sample_case["id"], "A").json()
    e2 = _create_entity(client, sample_case["id"], "B").json()

    rel = client.post(
        f"/api/cases/{sample_case['id']}/relationships",
        json={
            "source_entity_id": e1["id"],
            "target_entity_id": e2["id"],
            "relationship_type": "RELATED_TO",
        },
    ).json()

    resp = client.delete(f"/api/relationships/{rel['id']}")
    assert resp.status_code == 204

    resp = client.get(f"/api/relationships/{rel['id']}")
    assert resp.status_code == 404


def test_get_graph(client, sample_case):
    e1 = _create_entity(client, sample_case["id"], "A").json()
    e2 = _create_entity(client, sample_case["id"], "B").json()

    client.post(
        f"/api/cases/{sample_case['id']}/relationships",
        json={
            "source_entity_id": e1["id"],
            "target_entity_id": e2["id"],
            "relationship_type": "RELATED_TO",
        },
    )

    resp = client.get(f"/api/cases/{sample_case['id']}/graph")
    assert resp.status_code == 200
    graph = resp.json()

    assert len(graph["nodes"]) == 2
    assert len(graph["edges"]) == 1

    node = next(n for n in graph["nodes"] if n["data"]["label"] == "A")
    assert node["data"]["id"] == f"e{e1['id']}"
    assert node["data"]["type"] == "PERSON"

    edge = graph["edges"][0]
    assert edge["data"]["id"].startswith("r")
    assert edge["data"]["source"] == f"e{e1['id']}"
    assert edge["data"]["target"] == f"e{e2['id']}"
    assert edge["data"]["type"] == "RELATED_TO"


def test_get_graph_empty(client, sample_case):
    resp = client.get(f"/api/cases/{sample_case['id']}/graph")
    assert resp.status_code == 200
    assert resp.json() == {"nodes": [], "edges": []}


def test_get_graph_case_not_found(client):
    resp = client.get("/api/cases/9999/graph")
    assert resp.status_code == 404

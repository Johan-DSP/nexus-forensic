import sys
import os
import uuid
import hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path

# -----------------------------------------------------------------
# Detección automática del layout (dev vs Docker)
# -----------------------------------------------------------------
_HERE = Path(__file__).resolve()
_PROJECT_ROOT = _HERE.parent.parent

# Layout dev: <project>/scripts/seed_demo.py → <project>/backend/app
_DEV_BACKEND = _PROJECT_ROOT / "backend"
# Layout Docker: /app/scripts/seed_demo.py → /app/app
_DOCKER_BACKEND = _PROJECT_ROOT

_backend_candidate = None
for candidate in (_DEV_BACKEND, _DOCKER_BACKEND):
    if (candidate / "app" / "__init__.py").exists():
        _backend_candidate = candidate
        break

if _backend_candidate is None:
    raise RuntimeError(
        f"Cannot find `app` package. Tried: {_DEV_BACKEND}, {_DOCKER_BACKEND}"
    )

sys.path.insert(0, str(_backend_candidate))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.db.base import Base
from app.core.config import settings
from app.db.models.case import Case, CaseStatus
from app.db.models.nexus import Entity, Relationship, EntityType, RelationshipType
from app.db.models.chrono import Event, EventType, Certainty
from app.db.models.evidentia import Evidence


def clear_database():
    """Limpia la base de datos para una demostración limpia"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def create_demo_case(db: Session) -> Case:
    demo_case = Case(
        case_number="CASO-2026-DEMO",
        title="Operación Fénix - Demo",
        description=(
            "Caso ficticio autogenerado para demostración de capacidades "
            "del sistema NEXUS FORENSIC."
        ),
        status=CaseStatus.IN_PROGRESS,
    )
    db.add(demo_case)
    db.commit()
    db.refresh(demo_case)
    return demo_case


def seed_data():
    clear_database()
    db: Session = SessionLocal()

    try:
        print("Iniciando generación de datos de demostración...")

        # 1. Crear Caso
        case = create_demo_case(db)
        print(f"✓ Caso creado: {case.case_number}")

        # 2. Crear Entidades
        entities_data = [
            {
                "type": EntityType.PERSON,
                "name": "Alejandro Vargas",
                "identifier": "ID-001",
            },
            {
                "type": EntityType.PERSON,
                "name": "Sofía Mendoza",
                "identifier": "ID-002",
            },
            {
                "type": EntityType.PERSON,
                "name": "Carlos Rivera",
                "identifier": "ID-003",
            },
            {"type": EntityType.PERSON, "name": "Elena Rojas", "identifier": "ID-004"},
            {"type": EntityType.PERSON, "name": "Javier Silva", "identifier": "ID-005"},
            {"type": EntityType.PERSON, "name": "Marina Cruz", "identifier": "ID-006"},
            {"type": EntityType.PERSON, "name": "Roberto Luna", "identifier": "ID-007"},
            {
                "type": EntityType.PERSON,
                "name": "Desconocido (Alias 'Sombra')",
                "identifier": "ID-UNKNOWN",
            },
            {
                "type": EntityType.VEHICLE,
                "name": "Toyota Hilux Negra",
                "identifier": "ABC-123",
            },
            {
                "type": EntityType.VEHICLE,
                "name": "Honda Civic Gris",
                "identifier": "XYZ-987",
            },
            {
                "type": EntityType.VEHICLE,
                "name": "Ford Explorer Azul",
                "identifier": "DEF-456",
            },
            {
                "type": EntityType.VEHICLE,
                "name": "Motocicleta Yamaha",
                "identifier": "MOTO-01",
            },
            {
                "type": EntityType.PHONE,
                "name": "Móvil Principal Vargas",
                "identifier": "555-0101",
            },
            {
                "type": EntityType.PHONE,
                "name": "Móvil Prepago 1",
                "identifier": "555-0202",
            },
            {
                "type": EntityType.PHONE,
                "name": "Móvil Empresa",
                "identifier": "555-0303",
            },
            {
                "type": EntityType.ORGANIZATION,
                "name": "Logística Internacional S.A.",
                "identifier": "ORG-01",
            },
            {
                "type": EntityType.ORGANIZATION,
                "name": "Transportes Rápidos",
                "identifier": "ORG-02",
            },
            {
                "type": EntityType.LOCATION,
                "name": "Bodega Zona Norte",
                "identifier": "LOC-01",
            },
            {
                "type": EntityType.LOCATION,
                "name": "Oficina Central",
                "identifier": "LOC-02",
            },
            {
                "type": EntityType.LOCATION,
                "name": "Puerto de Carga",
                "identifier": "LOC-03",
            },
            {
                "type": EntityType.LOCATION,
                "name": "Residencia Vargas",
                "identifier": "LOC-04",
            },
            {
                "type": EntityType.LOCATION,
                "name": "Cafetería 'El Refugio'",
                "identifier": "LOC-05",
            },
        ]

        entities = []
        for ed in entities_data:
            e = Entity(**ed, case_id=case.id)
            db.add(e)
            entities.append(e)
        db.commit()

        # Referencias rápidas
        p_vargas, p_sofia, p_carlos, p_elena, p_javier = (
            entities[0],
            entities[1],
            entities[2],
            entities[3],
            entities[4],
        )
        v_hilux, v_civic = entities[8], entities[9]
        t_vargas, t_prepago = entities[12], entities[13]
        o_logistica = entities[15]
        l_bodega, l_puerto = entities[17], entities[19]

        # 3. Crear Relaciones
        rels = [
            (p_vargas.id, o_logistica.id, RelationshipType.EMPLOYED_BY),
            (p_sofia.id, o_logistica.id, RelationshipType.EMPLOYED_BY),
            (p_vargas.id, v_hilux.id, RelationshipType.OWNS),
            (p_carlos.id, v_civic.id, RelationshipType.USES),
            (p_vargas.id, t_vargas.id, RelationshipType.OWNS),
            (p_javier.id, t_prepago.id, RelationshipType.OWNS),
            (p_elena.id, l_bodega.id, RelationshipType.LOCATED_AT),
            (v_hilux.id, l_bodega.id, RelationshipType.LOCATED_AT),
            (p_vargas.id, p_sofia.id, RelationshipType.ASSOCIATED_WITH),
            (p_carlos.id, p_javier.id, RelationshipType.CONNECTED_TO),
            (t_vargas.id, t_prepago.id, RelationshipType.CONTACTED),
            (o_logistica.id, l_puerto.id, RelationshipType.ASSOCIATED_WITH),
            (p_sofia.id, l_puerto.id, RelationshipType.LOCATED_AT),
            (v_civic.id, l_puerto.id, RelationshipType.LOCATED_AT),
            (p_vargas.id, p_carlos.id, RelationshipType.RELATED_TO),
        ]

        for src, tgt, r_type in rels:
            db.add(
                Relationship(
                    case_id=case.id,
                    source_entity_id=src,
                    target_entity_id=tgt,
                    relationship_type=r_type,
                )
            )
        db.commit()
        print("✓ 22 Entidades y 15 Relaciones creadas.")

        # 4. Crear Eventos
        base_date = datetime(2026, 8, 30, 8, 0, tzinfo=timezone.utc)
        events_data = [
            {
                "title": "Llamada inicial",
                "type": EventType.CALL,
                "minutes_offset": 0,
                "duration": 5,
                "cert": Certainty.CONFIRMED,
            },
            {
                "title": "Movimiento de vehículo",
                "type": EventType.MOVEMENT,
                "minutes_offset": 30,
                "duration": 45,
                "cert": Certainty.CONFIRMED,
            },
            {
                "title": "Reunión en bodega",
                "type": EventType.MEETING,
                "minutes_offset": 60,
                "duration": 30,
                "cert": Certainty.REPORTED,
            },
            {
                "title": "Transacción sospechosa",
                "type": EventType.TRANSACTION,
                "minutes_offset": 120,
                "duration": 10,
                "cert": Certainty.ESTIMATED,
            },
            {
                "title": "Mensaje interceptado",
                "type": EventType.MESSAGE,
                "minutes_offset": 125,
                "duration": 1,
                "cert": Certainty.CONFIRMED,
            },
            {
                "title": "Observación en puerto",
                "type": EventType.OBSERVATION,
                "minutes_offset": 180,
                "duration": 120,
                "cert": Certainty.REPORTED,
            },
            {
                "title": "Llegada de camión",
                "type": EventType.MOVEMENT,
                "minutes_offset": 200,
                "duration": 15,
                "cert": Certainty.CONFIRMED,
            },
            {
                "title": "Llamada prepago",
                "type": EventType.CALL,
                "minutes_offset": 240,
                "duration": 8,
                "cert": Certainty.CONFIRMED,
            },
            {
                "title": "Firma de documento",
                "type": EventType.DOCUMENT,
                "minutes_offset": 300,
                "duration": 5,
                "cert": Certainty.CONFIRMED,
            },
            {
                "title": "Incidente reportado",
                "type": EventType.INCIDENT,
                "minutes_offset": 360,
                "duration": 60,
                "cert": Certainty.REPORTED,
            },
            {
                "title": "Huida del lugar",
                "type": EventType.MOVEMENT,
                "minutes_offset": 380,
                "duration": 20,
                "cert": Certainty.ESTIMATED,
            },
            {
                "title": "Cierre de operaciones",
                "type": EventType.OTHER,
                "minutes_offset": 450,
                "duration": 10,
                "cert": Certainty.CONFIRMED,
            },
        ]

        for ev in events_data:
            start = base_date + timedelta(minutes=ev["minutes_offset"])
            end = start + timedelta(minutes=ev["duration"])
            db.add(
                Event(
                    case_id=case.id,
                    title=ev["title"],
                    event_type=ev["type"],
                    start_datetime=start,
                    end_datetime=end,
                    certainty=ev["cert"],
                )
            )
        db.commit()
        print("✓ 12 Eventos cronológicos creados.")

        # 5. Crear Evidencias Ficticias
        storage_dir = settings.STORAGE_PATH
        os.makedirs(storage_dir, exist_ok=True)

        for i in range(1, 6):
            dummy_filename = f"evidencia_dummy_0{i}.txt"
            stored_name = f"{uuid.uuid4().hex}.txt"
            storage_path = os.path.join(storage_dir, stored_name)

            content = f"Archivo de evidencia generado para demostración. ID: {i}"

            with open(storage_path, "w") as f:
                f.write(content)

            h = hashlib.sha256(content.encode()).hexdigest()

            db.add(
                Evidence(
                    case_id=case.id,
                    original_filename=dummy_filename,
                    stored_filename=stored_name,
                    mime_type="text/plain",
                    file_size=len(content),
                    sha256=h,
                    storage_path=storage_path,
                    description=f"Evidencia simulada {i} recolectada en el sitio.",
                )
            )
        db.commit()
        print("✓ 5 Evidencias físicas creadas en storage y registradas en DB.")

        print("\n¡DEMO GENERADA CON ÉXITO!")

    except Exception as e:
        print(f"Error generando demo: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()

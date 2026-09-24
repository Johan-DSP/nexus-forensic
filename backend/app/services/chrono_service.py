from typing import List
from app.db.models.chrono import Event


def detect_overlaps(events: List[Event]) -> List[dict]:
    overlaps = []
    # Filtrar solo eventos que tengan inicio y fin
    valid_events = [e for e in events if e.start_datetime and e.end_datetime]

    # Comparar todos contra todos (O(n^2) aceptable para eventos de un caso local)
    for i in range(len(valid_events)):
        for j in range(i + 1, len(valid_events)):
            e1 = valid_events[i]
            e2 = valid_events[j]

            latest_start = max(e1.start_datetime, e2.start_datetime)
            earliest_end = min(e1.end_datetime, e2.end_datetime)

            delta = (earliest_end - latest_start).total_seconds()

            if delta > 0:  # Hay solapamiento
                overlaps.append(
                    {
                        "event_1_id": e1.id,
                        "event_2_id": e2.id,
                        "overlap_minutes": round(delta / 60, 2),
                        "message": "POSIBLE SOLAPAMIENTO TEMPORAL",
                    }
                )

    return overlaps

"""Neo4j 라벨 노드(=Concept) bulk upsert."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict
from typing import Any

from neo4j import Session

from app.ontology.domain.concepts import AnyConcept


def _props_of(concept: AnyConcept) -> dict[str, Any]:
    raw = asdict(concept)
    cleaned: dict[str, Any] = {}
    for k, v in raw.items():
        if v is None:
            continue
        if isinstance(v, tuple):
            v = list(v)
        cleaned[k] = v
    return cleaned


def bulk_upsert_concepts(
    session: Session, concepts: Sequence[AnyConcept]
) -> int:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for c in concepts:
        grouped.setdefault(type(c).LABEL, []).append(
            {"key": c.key, "props": _props_of(c)}
        )

    total = 0
    for label, rows in grouped.items():
        cypher = (
            "UNWIND $rows AS row "
            f"MERGE (n:`{label}` {{key: row.key}}) "
            "SET n += row.props"
        )
        session.run(cypher, rows=rows)
        total += len(rows)
    return total

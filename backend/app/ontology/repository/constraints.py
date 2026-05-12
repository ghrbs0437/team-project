"""Neo4j 스키마 제약 (라벨별 unique key)."""

from __future__ import annotations

from neo4j import Session

from app.ontology.util.concept_lookup import CONCEPT_REGISTRY


def ensure_constraints(session: Session) -> None:
    """각 concept 라벨에 (key) 유니크 제약을 멱등하게 생성."""
    for cls in CONCEPT_REGISTRY:
        label = cls.LABEL
        constraint_name = f"concept_{label.lower()}_key"
        cypher = (
            f"CREATE CONSTRAINT {constraint_name} IF NOT EXISTS "
            f"FOR (n:`{label}`) REQUIRE n.key IS UNIQUE"
        )
        session.run(cypher)

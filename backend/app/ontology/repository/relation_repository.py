"""Neo4j 관계 bulk upsert (concept-concept 3종 + user-concept 11종, 총 14종)."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict
from typing import Any

from neo4j import Session

from app.ontology.domain.relations import (
    AnyRelation,
    HasAvailabilityRelation,
    HasEducationRelation,
    HasExperienceTypeRelation,
    HasSkillRelation,
    HoldsCertificationRelation,
    InterestedInDomainRelation,
    LocatedInRelation,
    PlaysRoleRelation,
    PrefersWorkStyleRelation,
    PursuesGoalRelation,
    RelatedToRelation,
    RequiresRelation,
    UsesRelation,
    UsesTechnologyRelation,
)

_ALLOWED_REL_TYPES: frozenset[str] = frozenset({
    UsesRelation.REL_TYPE,
    RequiresRelation.REL_TYPE,
    RelatedToRelation.REL_TYPE,
    UsesTechnologyRelation.REL_TYPE,
    HasSkillRelation.REL_TYPE,
    PlaysRoleRelation.REL_TYPE,
    PursuesGoalRelation.REL_TYPE,
    InterestedInDomainRelation.REL_TYPE,
    HasAvailabilityRelation.REL_TYPE,
    PrefersWorkStyleRelation.REL_TYPE,
    HasExperienceTypeRelation.REL_TYPE,
    HasEducationRelation.REL_TYPE,
    HoldsCertificationRelation.REL_TYPE,
    LocatedInRelation.REL_TYPE,
})


def _rel_type_of(relation: AnyRelation) -> str:
    rel_type = getattr(type(relation), "REL_TYPE", None)
    if rel_type not in _ALLOWED_REL_TYPES:
        raise ValueError(f"Unknown relation class: {type(relation).__name__}")
    return rel_type


def _props_of(relation: AnyRelation) -> dict[str, Any]:
    raw = asdict(relation)
    raw.pop("source", None)
    raw.pop("target", None)
    return {k: v for k, v in raw.items() if v is not None}


def bulk_upsert_relations(
    session: Session, relations: Sequence[AnyRelation]
) -> int:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for r in relations:
        grouped.setdefault(_rel_type_of(r), []).append(
            {
                "source": r.source,
                "target": r.target,
                "props": _props_of(r),
            }
        )

    total = 0
    for rel_type, rows in grouped.items():
        cypher = (
            "UNWIND $rows AS row "
            "MATCH (a {key: row.source}) "
            "MATCH (b {key: row.target}) "
            f"MERGE (a)-[r:`{rel_type}`]->(b) "
            "SET r += row.props"
        )
        session.run(cypher, rows=rows)
        total += len(rows)
    return total

"""JSON 시드 데이터를 dataclass 인스턴스로 변환."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.ontology.domain.concepts import AnyConcept, _BaseConcept
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
from app.ontology.util.concept_lookup import class_by_json_key

# parents[3] == backend/, 거기에 data/ontology 를 붙임
_DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "ontology"
_CONCEPTS_PATH = _DATA_DIR / "concept.json"
_RELATIONS_PATH = _DATA_DIR / "relation.json"

_RELATION_CLASSES: dict[str, type[AnyRelation]] = {
    "uses": UsesRelation,
    "requires": RequiresRelation,
    "related_to": RelatedToRelation,
    "uses_technology": UsesTechnologyRelation,
    "has_skill": HasSkillRelation,
    "plays_role": PlaysRoleRelation,
    "pursues_goal": PursuesGoalRelation,
    "interested_in_domain": InterestedInDomainRelation,
    "has_availability": HasAvailabilityRelation,
    "prefers_work_style": PrefersWorkStyleRelation,
    "has_experience_type": HasExperienceTypeRelation,
    "has_education": HasEducationRelation,
    "holds_certification": HoldsCertificationRelation,
    "located_in": LocatedInRelation,
}


def _filter_fields(cls: type[_BaseConcept], entry: dict[str, Any]) -> dict[str, Any]:
    allowed = {f for f in cls.__dataclass_fields__}
    return {k: v for k, v in entry.items() if k in allowed}


def load_concepts(path: Path | None = None) -> list[AnyConcept]:
    raw = json.loads((path or _CONCEPTS_PATH).read_text(encoding="utf-8"))
    concepts: list[AnyConcept] = []
    for category_key, entries in raw.items():
        cls = class_by_json_key(category_key)
        if cls is None:
            raise ValueError(f"Unknown concept category in JSON: {category_key!r}")
        for entry in entries:
            concepts.append(cls(**_filter_fields(cls, entry)))
    return concepts


def load_relations(path: Path | None = None) -> list[AnyRelation]:
    raw = json.loads((path or _RELATIONS_PATH).read_text(encoding="utf-8"))
    relations: list[AnyRelation] = []
    for rel_key, entries in raw.items():
        cls = _RELATION_CLASSES.get(rel_key)
        if cls is None:
            raise ValueError(f"Unknown relation type in JSON: {rel_key!r}")
        for entry in entries:
            relations.append(cls(**_filter_fields(cls, entry)))
    return relations

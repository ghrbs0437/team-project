"""문자열 → concept 클래스 매핑 (JSON 로더 공용)."""

from __future__ import annotations

from app.ontology.domain.concepts import (
    AvailabilityConcept,
    CertificationConcept,
    DomainConcept,
    EducationConcept,
    ExperienceTypeConcept,
    GoalConcept,
    LocationConcept,
    RoleConcept,
    SkillConcept,
    TechnologyConcept,
    UserConcept,
    WorkStyleConcept,
    _BaseConcept,
)

CONCEPT_REGISTRY: tuple[type[_BaseConcept], ...] = (
    TechnologyConcept,
    SkillConcept,
    RoleConcept,
    DomainConcept,
    GoalConcept,
    AvailabilityConcept,
    WorkStyleConcept,
    ExperienceTypeConcept,
    EducationConcept,
    CertificationConcept,
    LocationConcept,
    UserConcept,
)

# JSON top-level 키 (snake_case) → 클래스. concepts.json 의 카테고리 키와 1:1.
_BY_JSON_KEY: dict[str, type[_BaseConcept]] = {
    "technology": TechnologyConcept,
    "skill": SkillConcept,
    "role": RoleConcept,
    "domain": DomainConcept,
    "goal": GoalConcept,
    "availability": AvailabilityConcept,
    "work_style": WorkStyleConcept,
    "experience_type": ExperienceTypeConcept,
    "education": EducationConcept,
    "certification": CertificationConcept,
    "location": LocationConcept,
    "user": UserConcept,
}

# Neo4j 라벨 (CamelCase) → 클래스. registry 에서 자동 derive.
_BY_LABEL: dict[str, type[_BaseConcept]] = {c.LABEL: c for c in CONCEPT_REGISTRY}


# ── 공개 조회 함수 ────────────────────────────────────────────────────────────

def class_by_json_key(key: str) -> type[_BaseConcept] | None:
    return _BY_JSON_KEY.get(key)


def class_by_label(label: str) -> type[_BaseConcept] | None:
    return _BY_LABEL.get(label)

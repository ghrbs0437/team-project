"""
개발자 프로필 온톨로지 타입 정의.

각 클래스에 LABEL ClassVar 가 Neo4j 라벨(CamelCase) 을 직접 보관한다.
relations.py 의 REL_TYPE 패턴과 대칭.

JSON·문자열 → 클래스 매핑은 app/ontology/util/concept_lookup.py 참고.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar, Literal


# ── 공통 베이스 ───────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class _BaseConcept:
    key: str
    name: str
    aliases: list[str] = field(default_factory=list)
    description: str | None = None


# ── 개념 유형별 클래스 ────────────────────────────────────────────────────────

@dataclass(frozen=True)
class TechnologyConcept(_BaseConcept):
    LABEL: ClassVar[str] = "Technology"
    category: str = ""
    subcategory: str | None = None
    license: Literal["open_source", "proprietary"] | None = None
    is_open_source: bool | None = None


@dataclass(frozen=True)
class SkillConcept(_BaseConcept):
    LABEL: ClassVar[str] = "Skill"
    difficulty: Literal["easy", "medium", "hard"] | None = None
    skill_type: Literal["soft", "technical", "cross_cutting"] | None = None


@dataclass(frozen=True)
class RoleConcept(_BaseConcept):
    LABEL: ClassVar[str] = "Role"
    typical_seniority: tuple[str, ...] = ()


@dataclass(frozen=True)
class GoalConcept(_BaseConcept):
    LABEL: ClassVar[str] = "Goal"
    goal_category: Literal["career", "business", "recognition", "financial"] | None = None


@dataclass(frozen=True)
class DomainConcept(_BaseConcept):
    LABEL: ClassVar[str] = "Domain"
    industry_sector: Literal[
        "tech", "finance", "healthcare", "education",
        "retail", "entertainment", "infrastructure", "other"
    ] | None = None


@dataclass(frozen=True)
class AvailabilityConcept(_BaseConcept):
    LABEL: ClassVar[str] = "Availability"
    hours_per_week_min: int | None = None
    hours_per_week_max: int | None = None


@dataclass(frozen=True)
class WorkStyleConcept(_BaseConcept):
    LABEL: ClassVar[str] = "WorkStyle"
    is_remote: bool | None = None


@dataclass(frozen=True)
class ExperienceTypeConcept(_BaseConcept):
    LABEL: ClassVar[str] = "ExperienceType"
    is_professional: bool | None = None


@dataclass(frozen=True)
class EducationConcept(_BaseConcept):
    LABEL: ClassVar[str] = "Education"
    credential_level: Literal["certificate", "undergraduate", "graduate"] | None = None
    duration_months: int | None = None


@dataclass(frozen=True)
class CertificationConcept(_BaseConcept):
    LABEL: ClassVar[str] = "Certification"
    issuing_org: str | None = None
    validity_years: int | None = None


@dataclass(frozen=True)
class LocationConcept(_BaseConcept):
    LABEL: ClassVar[str] = "Location"
    region: Literal["capital", "metropolitan", "provincial"] | None = None
    country: str = "KR"


@dataclass(frozen=True)
class UserConcept(_BaseConcept):
    """연수생 엔티티. user_id는 실제 사용자 식별자."""
    LABEL: ClassVar[str] = "User"
    user_id: int = 0


# ── 타입 별칭 ─────────────────────────────────────────────────────────────────

AnyConcept = (
    TechnologyConcept | SkillConcept | RoleConcept | DomainConcept | GoalConcept |
    AvailabilityConcept | WorkStyleConcept | ExperienceTypeConcept |
    EducationConcept | CertificationConcept | LocationConcept | UserConcept
)

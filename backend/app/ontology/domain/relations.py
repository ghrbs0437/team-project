"""
온톨로지 관계 타입 정의.

두 종류로 나뉜다:

1. 개념↔개념 관계 (concept-to-concept, 정적 taxonomy)
   - UsesRelation      USES         기술 의존성        (spring_boot → java)
   - RequiresRelation  REQUIRES     필수 선행 기술     (langchain → python)
   - RelatedToRelation RELATED_TO   유사/관련

2. 유저→개념 관계 (user-to-concept, extractor 가 raw_text 에서 추출)
   - 카테고리별 1:1 (UsesTechnologyRelation, HasSkillRelation 등 11종)
   - source = "user_{id}", target = concept key
   - 공통 메타: raw_evidence(원문 근거 문장), confidence(0.0–1.0, 근거 품질 기반)

Neo4j 적재는 repository/relation_repository.py 참고.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Literal


# ── 공통 베이스 ───────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class _BaseRelation:
    source: str
    target: str
    weight: float = 1.0


# ── 개념↔개념 관계 ───────────────────────────────────────────────────────────

@dataclass(frozen=True)
class UsesRelation(_BaseRelation):
    """A가 B를 런타임에 직접 사용/의존 (e.g. spring_boot → java)."""
    REL_TYPE: ClassVar[str] = "USES"


@dataclass(frozen=True)
class RequiresRelation(_BaseRelation):
    """A를 사용하려면 B가 선행되어야 함 (e.g. langchain → python).

    weight: 선행 필요 강도 (1.0 = 필수, 0.5 이하 = 선택적 권장)
    """
    REL_TYPE: ClassVar[str] = "REQUIRES"


@dataclass(frozen=True)
class RelatedToRelation(_BaseRelation):
    """A와 B가 유사하거나 관련됨. 단방향 저장, Cypher에서 무방향 조회.

    weight:   유사도 (1.0 = 매우 유사, 0.4 이하 = 느슨한 관련)
    category: 관계의 성격 분류
        competing        대체 가능한 경쟁 기술 (e.g. react ↔ vue)
        ecosystem        같은 생태계 내 연관 기술 (e.g. spring ↔ spring_boot)
        similar_language 문법·패러다임이 유사한 언어 (e.g. java ↔ kotlin)
        related_role     역할 간 연관성 (e.g. backend ↔ devops)
    """
    REL_TYPE: ClassVar[str] = "RELATED_TO"
    category: Literal[
        "competing",
        "ecosystem",
        "similar_language",
        "related_role",
    ] | None = None


# ── 유저→개념 관계 ───────────────────────────────────────────────────────────
#
# 모든 user-relation 은 다음 메타를 공통으로 가진다:
#   raw_evidence: LLM 이 해당 관계를 판단한 원문 표현/문장
#   confidence:   0.0–1.0. extractor 가 raw_evidence 의 품질로 산출
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class UsesTechnologyRelation(_BaseRelation):
    """유저가 특정 기술을 활용 (e.g. user_1 → python).

    proficiency: 숙련도
        expert       실무 운영·팀 리딩·프로덕션 배포가 명시
        advanced     1년 이상 프로젝트 경험 또는 깊이 있는 활용
        intermediate 학습 완료 또는 토이 프로젝트 경험
        beginner     관심·공부 중·기초·입문 수준
    years_of_experience: 명시된 경험 연수 (없으면 None)
    is_primary: 주력·메인 기술이면 True
    """
    REL_TYPE: ClassVar[str] = "USES_TECHNOLOGY"
    proficiency: Literal["beginner", "intermediate", "advanced", "expert"] | None = None
    years_of_experience: int | None = None
    is_primary: bool | None = None
    raw_evidence: str | None = None
    confidence: float | None = None


@dataclass(frozen=True)
class HasSkillRelation(_BaseRelation):
    """유저가 특정 역량을 보유 (e.g. user_1 → api_design).

    Skill 은 기술 스택과 별개의 메타 역량 (API 설계, 트러블슈팅, 팀 리딩 등).
    숙련도 메타는 없으며 raw_evidence 로 맥락을 보존.
    """
    REL_TYPE: ClassVar[str] = "HAS_SKILL"
    raw_evidence: str | None = None
    confidence: float | None = None


@dataclass(frozen=True)
class PlaysRoleRelation(_BaseRelation):
    """유저의 개발자 역할/포지션 (e.g. user_1 → backend).

    seniority: 시니어리티 (junior/mid/senior/lead). 언급 없으면 None
    is_current: 현재 포지션이면 True, 과거이면 False, 언급 없으면 None
    """
    REL_TYPE: ClassVar[str] = "PLAYS_ROLE"
    seniority: Literal["junior", "mid", "senior", "lead"] | None = None
    is_current: bool | None = None
    raw_evidence: str | None = None
    confidence: float | None = None


@dataclass(frozen=True)
class PursuesGoalRelation(_BaseRelation):
    """유저의 소마 활동 목표 (e.g. user_1 → portfolio).

    priority: 여러 목표 중 주된 목표면 primary, 보조면 secondary
    timeline: 단기 목표면 short, 장기면 long. 언급 없으면 None
    """
    REL_TYPE: ClassVar[str] = "PURSUES_GOAL"
    priority: Literal["primary", "secondary"] | None = None
    timeline: Literal["short", "long"] | None = None
    raw_evidence: str | None = None
    confidence: float | None = None


@dataclass(frozen=True)
class InterestedInDomainRelation(_BaseRelation):
    """유저의 관심 도메인·산업 (e.g. user_1 → finance_domain).

    interest_strength: 관심·전문성 강도
        strong   해당 도메인 경험·전문성 명시
        moderate 관심 또는 프로젝트 경험
        weak     단순 언급·관심 표현 수준
    """
    REL_TYPE: ClassVar[str] = "INTERESTED_IN_DOMAIN"
    interest_strength: Literal["weak", "moderate", "strong"] | None = None
    raw_evidence: str | None = None
    confidence: float | None = None


@dataclass(frozen=True)
class HasAvailabilityRelation(_BaseRelation):
    """유저의 시간 가용성 (e.g. user_1 → fulltime).

    가용 시간대·주당 시간 등의 카테고리는 target 의 AvailabilityConcept 노드가
    들고 있으며, 이 관계는 단순 연결만 표현한다.
    """
    REL_TYPE: ClassVar[str] = "HAS_AVAILABILITY"
    raw_evidence: str | None = None
    confidence: float | None = None


@dataclass(frozen=True)
class PrefersWorkStyleRelation(_BaseRelation):
    """유저의 협업·근무 방식 선호 (e.g. user_1 → remote).

    is_remote 같은 속성은 target WorkStyleConcept 노드에 있으며,
    유저는 그중 어떤 스타일을 선호하는지만 이 관계로 표현.
    """
    REL_TYPE: ClassVar[str] = "PREFERS_WORK_STYLE"
    raw_evidence: str | None = None
    confidence: float | None = None


@dataclass(frozen=True)
class HasExperienceTypeRelation(_BaseRelation):
    """유저가 가진 경험의 유형 (e.g. user_1 → project_experience).

    인턴·프로젝트·창업·해커톤 등 ExperienceTypeConcept 노드와 연결.
    개별 경험의 세부(프로젝트명·기술 스택 등) 는 별도 모델링 대상.
    """
    REL_TYPE: ClassVar[str] = "HAS_EXPERIENCE_TYPE"
    raw_evidence: str | None = None
    confidence: float | None = None


@dataclass(frozen=True)
class HasEducationRelation(_BaseRelation):
    """유저의 학력·교육 배경 (e.g. user_1 → cs_degree).

    credential_level(certificate/undergraduate/graduate) 은 target
    EducationConcept 의 속성이며, 이 관계는 유저↔교육이력 연결만 표현.
    """
    REL_TYPE: ClassVar[str] = "HAS_EDUCATION"
    raw_evidence: str | None = None
    confidence: float | None = None


@dataclass(frozen=True)
class HoldsCertificationRelation(_BaseRelation):
    """유저가 보유한 자격증 (e.g. user_1 → aws_saa).

    발급기관·유효기간 등은 target CertificationConcept 노드의 속성.
    """
    REL_TYPE: ClassVar[str] = "HOLDS_CERTIFICATION"
    raw_evidence: str | None = None
    confidence: float | None = None


@dataclass(frozen=True)
class LocatedInRelation(_BaseRelation):
    """유저의 거주지·활동 지역 (e.g. user_1 → seoul).

    region(capital/metropolitan/provincial)·country 등은 target
    LocationConcept 노드의 속성.
    """
    REL_TYPE: ClassVar[str] = "LOCATED_IN"
    raw_evidence: str | None = None
    confidence: float | None = None


# ── 타입 별칭 ─────────────────────────────────────────────────────────────────

AnyRelation = (
    UsesRelation | RequiresRelation | RelatedToRelation |
    UsesTechnologyRelation | HasSkillRelation | PlaysRoleRelation |
    PursuesGoalRelation | InterestedInDomainRelation |
    HasAvailabilityRelation | PrefersWorkStyleRelation |
    HasExperienceTypeRelation | HasEducationRelation |
    HoldsCertificationRelation | LocatedInRelation
)

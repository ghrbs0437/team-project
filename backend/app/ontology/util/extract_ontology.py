"""
raw_text → concept.json + relation.json 추출 스크립트.

OpenAI 호출로 각 유저의 raw_text 에서 온톨로지 개념·관계를 추출하고,
정적 온톨로지 (concepts.json/relations.json) 와 동일한 top-level grouping
구조로 backend/data/ontology/ 아래에 저장한다.

Usage:
    cd backend
    python -m app.ontology.util.extract_ontology              # 미추출 유저만
    python -m app.ontology.util.extract_ontology --force      # 전체 재추출
    python -m app.ontology.util.extract_ontology --user 1     # 단일 유저
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import fields
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv

from app.core.config import (
    get_upstage_api_key,
    get_upstage_base_url,
    get_upstage_model,
)
from app.core.database import SessionLocal
from app.ontology.domain.concepts import UserConcept
from app.ontology.domain.relations import (
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
    UsesTechnologyRelation,
)
from app.users.models import User

load_dotenv()


# ── 경로 ─────────────────────────────────────────────────────────────────────

_BACKEND_ROOT = Path(__file__).resolve().parents[3]
_DOMAIN_VALUE_DIR = Path(__file__).resolve().parent.parent / "domain" / "value"
_CONCEPTS_PATH = _DOMAIN_VALUE_DIR / "concepts.json"
_RELATIONS_PATH = _DOMAIN_VALUE_DIR / "relations.json"

OUTPUT_DIR = _BACKEND_ROOT / "data" / "ontology"
CONCEPT_OUTPUT_PATH = OUTPUT_DIR / "concept.json"
RELATION_OUTPUT_PATH = OUTPUT_DIR / "relation.json"


# ── concept_type → user-relation 클래스 ──────────────────────────────────────

_REL_FOR_CONCEPT_TYPE: dict[str, type] = {
    "technology": UsesTechnologyRelation,
    "skill": HasSkillRelation,
    "role": PlaysRoleRelation,
    "goal": PursuesGoalRelation,
    "domain": InterestedInDomainRelation,
    "availability": HasAvailabilityRelation,
    "work_style": PrefersWorkStyleRelation,
    "experience_type": HasExperienceTypeRelation,
    "education": HasEducationRelation,
    "certification": HoldsCertificationRelation,
    "location": LocatedInRelation,
}

# rel_type → JSON 키 (relation.json 의 top-level 키 = rel_type.lower())
_REL_JSON_KEY: dict[type, str] = {
    cls: cls.REL_TYPE.lower() for cls in _REL_FOR_CONCEPT_TYPE.values()
}

# 기본 필드(공통). 카테고리별 부가 필드는 dataclass introspection 으로 도출.
_COMMON_REL_FIELDS = frozenset({"source", "target", "weight", "raw_evidence", "confidence"})


# ── 카테고리별 한글 라벨 (프롬프트용) ────────────────────────────────────────

_CATEGORY_LABELS = {
    "technology":      "기술 스택 (언어, 프레임워크, DB, DevOps 등)",
    "skill":           "역량 (API 설계, 트러블슈팅, 팀 리딩 등)",
    "role":            "개발자 역할 (주력 포지션)",
    "goal":            "소마 활동 목표",
    "domain":          "관심 도메인/산업 분야",
    "availability":    "시간 가용성",
    "work_style":      "협업/근무 방식 선호",
    "experience_type": "경험 유형",
    "education":       "학력/교육 배경",
    "certification":   "자격증",
    "location":        "거주지/활동 지역",
}


# ── alias 인덱스 ─────────────────────────────────────────────────────────────

def _build_alias_index() -> tuple[dict[str, dict[str, str]], dict[str, list[str]]]:
    """concepts.json 을 읽어:
        - alias_index[category][alias_lower] = canonical_key
        - catalog[category]                  = canonical_key 리스트 (프롬프트용)
    """
    raw = json.loads(_CONCEPTS_PATH.read_text(encoding="utf-8"))
    alias_index: dict[str, dict[str, str]] = {}
    catalog: dict[str, list[str]] = {}
    for category, entries in raw.items():
        if category == "user":
            continue
        cat_idx: dict[str, str] = {}
        keys: list[str] = []
        for entry in entries:
            canonical = entry["key"]
            keys.append(canonical)
            cat_idx[canonical.lower()] = canonical
            name = entry.get("name")
            if isinstance(name, str):
                cat_idx[name.lower()] = canonical
            for alias in entry.get("aliases", []):
                if isinstance(alias, str):
                    cat_idx[alias.lower()] = canonical
        alias_index[category] = cat_idx
        catalog[category] = keys
    return alias_index, catalog


_ALIAS_INDEX, _CATALOG = _build_alias_index()


def _normalize(category: str, raw_value: str) -> str | None:
    idx = _ALIAS_INDEX.get(category)
    if idx is None:
        return None
    return idx.get(raw_value.strip().lower())


# ── 프롬프트 ─────────────────────────────────────────────────────────────────

_SYSTEM_INSTRUCTION = (
    "당신은 개발자 프로필 분석 전문가입니다. "
    "프로필 텍스트를 읽고 명시적으로 언급된 온톨로지 개념을 추출하세요. "
    "프로필에 없는 내용은 절대 추측하거나 추가하지 마세요. "
    "반드시 제공된 유효 값 목록에서만 선택하세요. "
    "응답은 반드시 JSON 객체로만 반환하세요."
)


_TYPE_SPECIFIC_INSTRUCTIONS = """
카테고리별 추가 필드 (해당되는 경우에만 포함, 언급이 없으면 null):

[technology]
  - proficiency: "beginner" | "intermediate" | "advanced" | "expert"
      expert:       실무 운영·팀 리딩·프로덕션 배포가 명시된 경우
      advanced:     1년 이상 프로젝트 경험 또는 깊이 있는 활용이 명시된 경우
      intermediate: 학습 완료 또는 토이 프로젝트 경험
      beginner:     관심·공부 중·기초·입문 수준
  - years_of_experience: 정수 (경험 연수가 명시된 경우만, 없으면 null)
  - is_primary: true | false (주력·메인 기술이면 true, 언급 없으면 false)

[role]
  - seniority: "junior" | "mid" | "senior" | "lead" (언급된 경우만, 없으면 null)
  - is_current: true | false (현재 포지션이면 true, 과거이면 false, 언급 없으면 null)

[domain]
  - interest_strength: "weak" | "moderate" | "strong"
      strong:   해당 도메인 경험·전문성이 명시된 경우
      moderate: 관심 또는 프로젝트 경험이 있는 경우
      weak:     단순 언급 또는 관심 표현 수준

[goal]
  - priority: "primary" | "secondary"
  - timeline: "short" | "long"
"""


def _build_prompt(raw_text: str) -> str:
    lines = [
        "다음 개발자 프로필에서 온톨로지 개념을 추출하세요.",
        "응답 형식:",
        "{",
        '  "concepts": {',
        '    "technology":      [{"value": "유효 값", "raw_evidence": "원문 근거", "proficiency": "advanced", "years_of_experience": 2, "is_primary": true}],',
        '    "role":            [{"value": "유효 값", "raw_evidence": "원문 근거", "seniority": "mid", "is_current": true}],',
        '    "domain":          [{"value": "유효 값", "raw_evidence": "원문 근거", "interest_strength": "strong"}],',
        '    "goal":            [{"value": "유효 값", "raw_evidence": "원문 근거", "priority": "primary", "timeline": "short"}],',
        '    "skill":           [{"value": "유효 값", "raw_evidence": "원문 근거"}],',
        '    "education":       [{"value": "유효 값", "raw_evidence": "원문 근거"}],',
        '    "experience_type": [{"value": "유효 값", "raw_evidence": "원문 근거"}],',
        '    "location":        [{"value": "유효 값", "raw_evidence": "원문 근거"}],',
        '    "availability": [], "work_style": [], "certification": []',
        "  }",
        "}",
        "concepts 는 명시적으로 언급된 항목만 담고, value 는 아래 유효 값 목록에서만 선택하세요.",
        "raw_evidence 에는 value 가 아니라 해당 개념을 판단한 원문 표현이나 원문 문장을 담으세요.",
        "confidence 는 포함하지 마세요. 추출기가 정규화 후 근거 품질로 계산합니다.",
        _TYPE_SPECIFIC_INSTRUCTIONS,
    ]
    for category, keys in _CATALOG.items():
        label = _CATEGORY_LABELS.get(category, category)
        lines.append(f"- {category} ({label}): {keys}")
    lines.append(f"\n프로필 텍스트:\n{raw_text}")
    return "\n".join(lines)


# ── OpenAI 호출 ──────────────────────────────────────────────────────────────

def _call_llm(raw_text: str) -> dict:
    """Upstage Solar API (OpenAI 호환) 호출 → 정규화 전 raw concepts dict 반환."""
    from openai import OpenAI  # 모듈 로드 시점 openai 미설치 허용 위해 지연 import
    client = OpenAI(
        api_key=get_upstage_api_key(),
        base_url=get_upstage_base_url(),
    )
    model = get_upstage_model()
    raw_output: dict[str, Any] = {}
    for attempt in range(4):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": _SYSTEM_INSTRUCTION},
                    {"role": "user", "content": _build_prompt(raw_text)},
                ],
                response_format={"type": "json_object"},
                temperature=0,
            )
            raw_output = json.loads(response.choices[0].message.content)
            break
        except Exception as e:
            if attempt < 3 and ("429" in str(e) or "503" in str(e) or "rate" in str(e).lower()):
                wait = 10 * (attempt + 1)
                print(f"[extract] {type(e).__name__} - {wait}초 후 재시도 ({attempt + 1}/3)")
                time.sleep(wait)
                continue
            raise

    raw_concepts = raw_output.get("concepts", raw_output)
    return raw_concepts if isinstance(raw_concepts, dict) else {}


# ── confidence 계산 ──────────────────────────────────────────────────────────

def _clamp(value: float) -> float:
    return round(max(0.0, min(value, 1.0)), 2)


def _concept_confidence(raw_value: str, raw_evidence: str, legacy_string: bool) -> float:
    if legacy_string:
        return 0.6
    nv = raw_value.strip().lower()
    ne = raw_evidence.strip().lower()
    if not ne:
        return 0.55
    if ne == nv:
        return 0.65
    confidence = 0.85
    if nv in ne:
        confidence += 0.05
    if any(ch.isspace() for ch in raw_evidence) or len(raw_evidence) >= len(raw_value) + 8:
        confidence += 0.05
    return _clamp(confidence)


def _clean_text(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


# ── 추출 결과 정규화 ────────────────────────────────────────────────────────

def _allowed_extra_fields(rel_cls: type) -> set[str]:
    return {f.name for f in fields(rel_cls) if f.name not in _COMMON_REL_FIELDS}


def _normalize_concepts(raw_concepts: dict) -> list[dict]:
    """LLM 출력 → [{concept_type, canonical, raw_evidence, confidence, **extras}]
    (concept_type, canonical) 별 dedup, confidence 최대값 보존."""
    by_key: dict[tuple[str, str], dict] = {}
    for concept_type, values in raw_concepts.items():
        rel_cls = _REL_FOR_CONCEPT_TYPE.get(concept_type)
        if rel_cls is None or not isinstance(values, list):
            continue
        allowed_extras = _allowed_extra_fields(rel_cls)

        for item in values:
            if isinstance(item, str):
                raw_value, raw_evidence, legacy = item, item, True
                extras: dict[str, Any] = {}
            elif isinstance(item, dict):
                raw_value = item.get("value")
                if not isinstance(raw_value, str):
                    continue
                evidence = _clean_text(item.get("raw_evidence")) or raw_value
                raw_evidence, legacy = evidence, False
                extras = {
                    k: item[k] for k in allowed_extras
                    if k in item and item[k] is not None
                }
            else:
                continue

            raw_value = raw_value.strip()
            if not raw_value:
                continue
            canonical = _normalize(concept_type, raw_value)
            if canonical is None:
                continue
            confidence = _concept_confidence(raw_value, raw_evidence, legacy)
            record = {
                "concept_type": concept_type,
                "canonical": canonical,
                "raw_evidence": raw_evidence,
                "confidence": confidence,
                "extras": extras,
            }
            existing = by_key.get((concept_type, canonical))
            if existing is None or confidence > existing["confidence"]:
                by_key[(concept_type, canonical)] = record
    return list(by_key.values())


# ── dataclass → 직렬화 dict ─────────────────────────────────────────────────

def _user_concept_dict(user: User) -> dict[str, Any]:
    concept = UserConcept(
        key=f"user_{user.id}",
        name=user.name,
        aliases=[],
        user_id=user.id,
    )
    return {
        "key": concept.key,
        "name": concept.name,
        "aliases": list(concept.aliases),
        "user_id": concept.user_id,
    }


def _user_relation_dict(
    user_id: int,
    record: dict[str, Any],
) -> tuple[str, dict[str, Any]] | None:
    rel_cls = _REL_FOR_CONCEPT_TYPE.get(record["concept_type"])
    if rel_cls is None:
        return None

    base: dict[str, Any] = {
        "source": f"user_{user_id}",
        "target": record["canonical"],
        "weight": 1.0,
        "raw_evidence": record["raw_evidence"],
        "confidence": record["confidence"],
    }
    base.update(record["extras"])
    return _REL_JSON_KEY[rel_cls], base


# ── 파일 IO + 유저 단위 멱등 upsert ──────────────────────────────────────────

def _load_concepts() -> dict[str, list[dict]]:
    """Static taxonomy(`domain/concepts.json`) 베이스 + 기존 출력의 user 섹션 보존.

    output 파일을 자체 시드 가능한 graph snapshot 으로 유지하기 위해 매번 정적
    taxonomy 를 새로 로드한다 (static 갱신을 즉시 반영). user 섹션만 덮어쓰지 않음.
    """
    data = json.loads(_CONCEPTS_PATH.read_text(encoding="utf-8"))
    data.setdefault("user", [])
    if CONCEPT_OUTPUT_PATH.exists():
        existing = json.loads(CONCEPT_OUTPUT_PATH.read_text(encoding="utf-8"))
        if isinstance(existing.get("user"), list):
            data["user"] = existing["user"]
    return data


def _save_concepts(data: dict[str, list[dict]]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CONCEPT_OUTPUT_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _load_relations() -> dict[str, list[dict]]:
    """Static taxonomy(`domain/relations.json`) 베이스 + 기존 출력의 user-rel 섹션 보존."""
    data = json.loads(_RELATIONS_PATH.read_text(encoding="utf-8"))
    for key in _REL_JSON_KEY.values():
        data.setdefault(key, [])

    if RELATION_OUTPUT_PATH.exists():
        existing = json.loads(RELATION_OUTPUT_PATH.read_text(encoding="utf-8"))
        for key in _REL_JSON_KEY.values():
            if isinstance(existing.get(key), list):
                data[key] = existing[key]
    return data


def _save_relations(data: dict[str, list[dict]]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RELATION_OUTPUT_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _upsert_user_concept(data: dict[str, list[dict]], user_dict: dict) -> None:
    section = data.setdefault("user", [])
    user_key = user_dict["key"]
    data["user"] = [e for e in section if e.get("key") != user_key]
    data["user"].append(user_dict)


def _upsert_user_relations(
    data: dict[str, list[dict]],
    user_id: int,
    new_entries: list[tuple[str, dict[str, Any]]],
) -> None:
    """user_{id} 가 source 인 모든 기존 entries 를 모든 섹션에서 제거 후 새로 append."""
    source_key = f"user_{user_id}"

    for rel_json_key in _REL_JSON_KEY.values():
        section = data.setdefault(rel_json_key, [])
        data[rel_json_key] = [e for e in section if e.get("source") != source_key]

    for rel_json_key, entry in new_entries:
        data.setdefault(rel_json_key, []).append(entry)


# ── 추출 진입점 ──────────────────────────────────────────────────────────────

def _extract_for_user(user: User) -> tuple[dict, list[tuple[str, dict]]]:
    raw_concepts = _call_llm(user.raw_text or "")
    normalized = _normalize_concepts(raw_concepts)

    user_concept = _user_concept_dict(user)
    relations: list[tuple[str, dict]] = []
    for record in normalized:
        item = _user_relation_dict(user.id, record)
        if item is not None:
            relations.append(item)
    return user_concept, relations


def extract_user(user_id: int) -> tuple[int, int]:
    """단일 유저 추출 → 두 파일 갱신. (concepts_count, relations_count) 반환."""
    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        if user is None:
            raise ValueError(f"user_id={user_id} not found")
        if not user.raw_text:
            raise ValueError(f"user_id={user_id} has no raw_text")
        user_concept, relations = _extract_for_user(user)
    finally:
        db.close()

    concept_data = _load_concepts()
    _upsert_user_concept(concept_data, user_concept)
    _save_concepts(concept_data)

    relation_data = _load_relations()
    _upsert_user_relations(relation_data, user_id, relations)
    _save_relations(relation_data)

    return 1, len(relations)


def extract_batch(force: bool = False) -> dict[str, int]:
    db = SessionLocal()
    try:
        users = (
            db.query(User)
            .filter(User.raw_text.isnot(None))
            .order_by(User.id)
            .all()
        )
        user_records = [(u.id, u.name, u.raw_text) for u in users]
    finally:
        db.close()

    concept_data = _load_concepts()
    relation_data = _load_relations()
    existing_user_keys = {e.get("key") for e in concept_data.get("user", [])}

    result = {"total": 0, "success": 0, "failed": 0, "skipped": 0}

    for user_id, name, raw_text in user_records:
        user_key = f"user_{user_id}"
        if not force and user_key in existing_user_keys:
            result["skipped"] += 1
            continue

        result["total"] += 1
        try:
            shim = User(id=user_id, name=name, raw_text=raw_text)
            user_concept, relations = _extract_for_user(shim)

            _upsert_user_concept(concept_data, user_concept)
            _upsert_user_relations(relation_data, user_id, relations)
            _save_concepts(concept_data)
            _save_relations(relation_data)

            result["success"] += 1
            print(
                f"[extract] user_id={user_id} 완료 "
                f"(relations={len(relations)}, {result['success']}/{result['total']})"
            )
        except Exception as e:
            print(f"[extract] user_id={user_id} 실패: {e}")
            result["failed"] += 1

    return result


# ── CLI ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="raw_text → concept.json + relation.json 추출"
    )
    parser.add_argument("--force", action="store_true",
                        help="기존 데이터가 있어도 재추출")
    parser.add_argument("--user", type=int, help="단일 유저 ID 추출")
    args = parser.parse_args()

    if args.user:
        concepts_count, relations_count = extract_user(args.user)
        print(
            f"완료: user_id={args.user}, "
            f"concept={concepts_count}, relations={relations_count}\n"
            f"  → {CONCEPT_OUTPUT_PATH}\n"
            f"  → {RELATION_OUTPUT_PATH}"
        )
    else:
        result = extract_batch(force=args.force)
        print(
            f"\n완료 - total={result['total']}, "
            f"success={result['success']}, "
            f"failed={result['failed']}, "
            f"skipped={result['skipped']}"
        )
        print(f"  → {CONCEPT_OUTPUT_PATH}")
        print(f"  → {RELATION_OUTPUT_PATH}")


if __name__ == "__main__":
    main()

"""Neo4j 온톨로지 repository 공개 API."""

from app.ontology.repository.concept_repository import bulk_upsert_concepts
from app.ontology.repository.constraints import ensure_constraints
from app.ontology.repository.relation_repository import bulk_upsert_relations

__all__ = [
    "ensure_constraints",
    "bulk_upsert_concepts",
    "bulk_upsert_relations",
]

"""Neo4j에 온톨로지 시드 데이터를 적재.

실행:
    cd backend
    python -m scripts.seed_ontology
"""

from __future__ import annotations

from dotenv import load_dotenv

from app.core.neo4j import close_driver, get_driver
from app.ontology.repository import (
    bulk_upsert_concepts,
    bulk_upsert_relations,
    ensure_constraints,
)
from app.ontology.util.loaders import load_concepts, load_relations


def main() -> None:
    load_dotenv()
    driver = get_driver()
    try:
        with driver.session(database="neo4j") as session:
            print("[1/4] ensuring constraints...")
            ensure_constraints(session)

            print("[2/4] loading concept JSON...")
            concepts = load_concepts()
            print(f"       loaded {len(concepts)} concepts from JSON")

            print("[3/4] upserting concepts into Neo4j...")
            inserted_concepts = bulk_upsert_concepts(session, concepts)
            print(f"       upserted {inserted_concepts} concept rows")

            print("[4/4] loading & upserting relations...")
            relations = load_relations()
            inserted_relations = bulk_upsert_relations(session, relations)
            print(
                f"       upserted {inserted_relations} relations "
                f"(from {len(relations)} JSON entries)"
            )

            print("\n=== counts per label ===")
            result = session.run(
                "MATCH (n) RETURN labels(n)[0] AS label, count(*) AS c "
                "ORDER BY label"
            )
            for record in result:
                print(f"  {record['label']:<20} {record['c']}")

            print("\n=== counts per relation type ===")
            result = session.run(
                "MATCH ()-[r]->() RETURN type(r) AS rel_type, count(*) AS c "
                "ORDER BY rel_type"
            )
            for record in result:
                print(f"  {record['rel_type']:<20} {record['c']}")
    finally:
        close_driver()


if __name__ == "__main__":
    main()

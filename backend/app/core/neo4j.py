from neo4j import Driver, GraphDatabase

from app.core.config import get_neo4j_password, get_neo4j_uri, get_neo4j_user

_driver: Driver | None = None


def get_driver() -> Driver:
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            get_neo4j_uri(),
            auth=(get_neo4j_user(), get_neo4j_password()),
        )
    return _driver


def close_driver() -> None:
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None

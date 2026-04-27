import os

import pandas as pd
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

_BATCH_SIZE = 1_000
_DATABASE = os.environ.get("NEO4J_DATABASE", "neo4j")


def get_driver():
    uri = os.environ["NEO4J_URI"]
    user = os.environ["NEO4J_USER"]
    password = os.environ["NEO4J_PASSWORD"]
    return GraphDatabase.driver(uri, auth=(user, password))


def ensure_constraints(driver) -> None:
    """Create uniqueness constraints on all node primary keys (idempotent)."""
    constraints = [
        ("Building", "bbl"),
        ("Complaint", "complaint_id"),
        ("Violation", "violation_id"),
        ("Registration", "registration_id"),
    ]
    with driver.session(database=_DATABASE) as session:
        for label, prop in constraints:
            session.run(
                f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) REQUIRE n.{prop} IS UNIQUE"
            )


def _batches(df: pd.DataFrame, size: int):
    for i in range(0, len(df), size):
        yield df.iloc[i : i + size].to_dict("records")


def load_buildings(driver, bbls: list[str]) -> int:
    """MERGE one Building node per unique BBL. Returns nodes written."""
    unique = list(set(b for b in bbls if b and pd.notna(b)))
    written = 0
    with driver.session(database=_DATABASE) as session:
        for i in range(0, len(unique), _BATCH_SIZE):
            batch = [{"bbl": b} for b in unique[i : i + _BATCH_SIZE]]
            result = session.run(
                "UNWIND $rows AS row "
                "MERGE (b:Building {bbl: row.bbl}) "
                "RETURN count(b) AS n",
                rows=batch,
            )
            written += result.single()["n"]
    return written


def load_complaints(driver, df: pd.DataFrame) -> tuple[int, int]:
    """MERGE Complaint nodes and [:FILED_AGAINST] relationships to Building.

    Returns (nodes_written, rels_written).
    """
    nodes, rels = 0, 0
    with driver.session(database=_DATABASE) as session:
        for batch in _batches(df, _BATCH_SIZE):
            result = session.run(
                "UNWIND $rows AS row "
                "MERGE (c:Complaint {complaint_id: row.unique_key}) "
                "  SET c += { "
                "    created_date: row.created_date, "
                "    closed_date: row.closed_date, "
                "    complaint_type: row.complaint_type, "
                "    descriptor: row.descriptor, "
                "    status: row.status, "
                "    borough: row.borough, "
                "    incident_address: row.incident_address, "
                "    bbl: row.bbl "
                "  } "
                "WITH c, row "
                "MATCH (b:Building {bbl: row.bbl}) "
                "MERGE (c)-[r:FILED_AGAINST]->(b) "
                "RETURN count(c) AS n, count(r) AS m",
                rows=batch,
            )
            record = result.single()
            nodes += record["n"]
            rels += record["m"]
    return nodes, rels


def load_violations(driver, df: pd.DataFrame) -> tuple[int, int]:
    """MERGE Violation nodes and [:FILED_AGAINST] relationships to Building.

    Returns (nodes_written, rels_written).
    """
    nodes, rels = 0, 0
    with driver.session(database=_DATABASE) as session:
        for batch in _batches(df, _BATCH_SIZE):
            result = session.run(
                "UNWIND $rows AS row "
                "MERGE (v:Violation {violation_id: row.violationid}) "
                "  SET v += { "
                "    inspection_date: row.inspectiondate, "
                "    approved_date: row.approveddate, "
                "    class: row.class, "
                "    type: row.violationtype, "
                "    status: row.violationstatus, "
                "    description: row.novdescription, "
                "    apartment: row.apartment, "
                "    story: row.story, "
                "    bbl: row.bbl "
                "  } "
                "WITH v, row "
                "MATCH (b:Building {bbl: row.bbl}) "
                "MERGE (v)-[r:FILED_AGAINST]->(b) "
                "RETURN count(v) AS n, count(r) AS m",
                rows=batch,
            )
            record = result.single()
            nodes += record["n"]
            rels += record["m"]
    return nodes, rels


def load_registrations(driver, df: pd.DataFrame) -> tuple[int, int]:
    """MERGE Registration nodes and [:REGISTERED_TO] relationships to Building.

    Returns (nodes_written, rels_written).
    """
    nodes, rels = 0, 0
    with driver.session(database=_DATABASE) as session:
        for batch in _batches(df, _BATCH_SIZE):
            result = session.run(
                "UNWIND $rows AS row "
                "MERGE (r:Registration {registration_id: row.registrationid}) "
                "  SET r += { "
                "    building_id: row.buildingid, "
                "    lifecycle_stage: row.lifecyclestage, "
                "    last_modified: row.lastmodifieddate, "
                "    owner_first_name: row.ownerfirstname, "
                "    owner_last_name: row.ownerlastname, "
                "    owner_type: row.ownertype, "
                "    bbl: row.bbl "
                "  } "
                "WITH r, row "
                "MATCH (b:Building {bbl: row.bbl}) "
                "MERGE (r)-[rel:REGISTERED_TO]->(b) "
                "RETURN count(r) AS n, count(rel) AS m",
                rows=batch,
            )
            record = result.single()
            nodes += record["n"]
            rels += record["m"]
    return nodes, rels

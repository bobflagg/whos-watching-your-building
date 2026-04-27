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
        ("Landlord", "registration_id"),
        ("Agency", "agency_code"),
        ("Inspection", "inspection_id"),
        ("Neighborhood", "ntacode"),
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


def load_building_addresses(driver, df: pd.DataFrame) -> int:
    """Enrich Building nodes with address fields. Uses COALESCE so existing values are never overwritten.

    Returns number of Building nodes touched.
    """
    written = 0
    with driver.session(database=_DATABASE) as session:
        for batch in _batches(df, _BATCH_SIZE):
            result = session.run(
                "UNWIND $rows AS row "
                "MATCH (b:Building {bbl: row.bbl}) "
                "SET b.borough         = COALESCE(b.borough,         row.boro), "
                "    b.house_number    = COALESCE(b.house_number,    row.housenumber), "
                "    b.street_name     = COALESCE(b.street_name,     row.streetname), "
                "    b.zip             = COALESCE(b.zip,             row.zip), "
                "    b.community_board = COALESCE(b.community_board, row.communityboard), "
                "    b.bin             = COALESCE(b.bin,             row.bin), "
                "    b.block           = COALESCE(b.block,           row.block), "
                "    b.lot             = COALESCE(b.lot,             row.lot) "
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
                "    resolution_description: row.resolution_description, "
                "    resolution_action_updated_date: row.resolution_action_updated_date, "
                "    borough: row.borough, "
                "    incident_address: row.incident_address, "
                "    community_board: row.community_board, "
                "    latitude: row.latitude, "
                "    longitude: row.longitude, "
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


def load_agencies(driver, df: pd.DataFrame) -> tuple[int, int]:
    """MERGE Agency nodes and [:HANDLED_BY] relationships from Complaint.

    Returns (nodes_written, rels_written).
    """
    nodes, rels = 0, 0
    agency_df = df[df["agency"].notna()].copy()
    with driver.session(database=_DATABASE) as session:
        for batch in _batches(agency_df, _BATCH_SIZE):
            result = session.run(
                "UNWIND $rows AS row "
                "MERGE (a:Agency {agency_code: row.agency}) "
                "  SET a.agency_name = row.agency_name "
                "WITH a, row "
                "MATCH (c:Complaint {complaint_id: row.unique_key}) "
                "MERGE (c)-[r:HANDLED_BY]->(a) "
                "RETURN count(DISTINCT a) AS n, count(r) AS m",
                rows=batch,
            )
            record = result.single()
            nodes += record["n"]
            rels += record["m"]
    return nodes, rels


def load_violations(driver, df: pd.DataFrame) -> tuple[int, int]:
    """MERGE Violation nodes and [:HAS_VIOLATION] relationships from Building.

    Returns (nodes_written, rels_written).
    """
    nodes, rels = 0, 0
    with driver.session(database=_DATABASE) as session:
        for batch in _batches(df, _BATCH_SIZE):
            result = session.run(
                "UNWIND $rows AS row "
                "MERGE (v:Violation {violation_id: row.violationid}) "
                "  SET v += { "
                "    class: row.class, "
                "    type: row.novtype, "
                "    status: row.violationstatus, "
                "    description: row.novdescription, "
                "    order_number: row.ordernumber, "
                "    nov_id: row.novid, "
                "    nov_issued_date: row.novissueddate, "
                "    current_status: row.currentstatus, "
                "    current_status_date: row.currentstatusdate, "
                "    rent_impairing: row.rentimpairing, "
                "    apartment: row.apartment, "
                "    story: row.story, "
                "    certify_by_date: row.newcertifybydate, "
                "    correct_by_date: row.newcorrectbydate, "
                "    bbl: row.bbl "
                "  } "
                "WITH v, row "
                "MATCH (b:Building {bbl: row.bbl}) "
                "MERGE (b)-[r:HAS_VIOLATION]->(v) "
                "RETURN count(v) AS n, count(r) AS m",
                rows=batch,
            )
            record = result.single()
            nodes += record["n"]
            rels += record["m"]
    return nodes, rels


def load_inspections(driver, df: pd.DataFrame) -> tuple[int, int]:
    """MERGE Inspection nodes and [:INSPECTED_BY] relationships from Violation.

    Returns (nodes_written, rels_written).
    """
    nodes, rels = 0, 0
    with driver.session(database=_DATABASE) as session:
        for batch in _batches(df, _BATCH_SIZE):
            result = session.run(
                "UNWIND $rows AS row "
                "MERGE (i:Inspection {inspection_id: row.violationid}) "
                "  SET i += { "
                "    inspection_date: row.inspectiondate, "
                "    approved_date: row.approveddate, "
                "    certified_date: row.certifieddate, "
                "    original_certify_by_date: row.originalcertifybydate, "
                "    original_correct_by_date: row.originalcorrectbydate "
                "  } "
                "WITH i, row "
                "MATCH (v:Violation {violation_id: row.violationid}) "
                "MERGE (v)-[r:INSPECTED_BY]->(i) "
                "RETURN count(i) AS n, count(r) AS m",
                rows=batch,
            )
            record = result.single()
            nodes += record["n"]
            rels += record["m"]
    return nodes, rels


def load_neighborhoods(driver, df: pd.DataFrame) -> tuple[int, int]:
    """MERGE Neighborhood nodes and [:LOCATED_IN] relationships from Building.

    Returns (nodes_written, rels_written).
    """
    nodes, rels = 0, 0
    nta_df = df[df["nta"].notna() & (df["nta"] != "")].copy()
    with driver.session(database=_DATABASE) as session:
        for batch in _batches(nta_df, _BATCH_SIZE):
            result = session.run(
                "UNWIND $rows AS row "
                "MERGE (n:Neighborhood {ntacode: row.nta}) "
                "  SET n.borough = row.boro "
                "WITH n, row "
                "MATCH (b:Building {bbl: row.bbl}) "
                "MERGE (b)-[r:LOCATED_IN]->(n) "
                "RETURN count(DISTINCT n) AS n, count(r) AS m",
                rows=batch,
            )
            record = result.single()
            nodes += record["n"]
            rels += record["m"]
    return nodes, rels


def load_registrations(driver, df: pd.DataFrame) -> tuple[int, int]:
    """MERGE Landlord nodes and [:OWNED_BY] relationships from Building.

    Returns (nodes_written, rels_written).
    """
    nodes, rels = 0, 0
    with driver.session(database=_DATABASE) as session:
        for batch in _batches(df, _BATCH_SIZE):
            result = session.run(
                "UNWIND $rows AS row "
                "MERGE (l:Landlord {registration_id: row.registrationid}) "
                "  SET l += { "
                "    building_id: row.buildingid, "
                "    last_registration_date: row.lastregistrationdate, "
                "    registration_end_date: row.registrationenddate, "
                "    bbl: row.bbl "
                "  } "
                "WITH l, row "
                "MATCH (b:Building {bbl: row.bbl}) "
                "MERGE (b)-[rel:OWNED_BY]->(l) "
                "RETURN count(l) AS n, count(rel) AS m",
                rows=batch,
            )
            record = result.single()
            nodes += record["n"]
            rels += record["m"]
    return nodes, rels

from src.graph.loader import (
    ensure_constraints,
    get_driver,
    load_buildings,
    load_complaints,
    load_registrations,
    load_violations,
)
from src.ingest.normalize import derive_bbl, normalize_bbl
from src.ingest.soda_client import fetch_all, fetch_recent_paginated, lookback_months

_311_DATASET = "erm2-nwe9"
_VIOLATIONS_DATASET = "wvxf-dwi5"
_REGISTRATIONS_DATASET = "tesw-yqqr"


def run() -> None:
    months = lookback_months()
    print(f"Lookback window: {months} months")

    # --- Fetch ---
    print("Fetching 311 HPD complaints (paginated)...")
    complaints = fetch_recent_paginated(
        _311_DATASET, "created_date", agency="HPD"
    )
    print(f"  {len(complaints):,} complaints fetched")

    print("Fetching HPD violations...")
    violations = fetch_recent_paginated(_VIOLATIONS_DATASET, "inspectiondate")
    print(f"  {len(violations):,} violations fetched")

    print("Fetching HPD registrations (full pull)...")
    registrations = fetch_all(_REGISTRATIONS_DATASET)
    print(f"  {len(registrations):,} registrations fetched")

    # --- Normalize BBL ---
    complaints["bbl"] = normalize_bbl(complaints["bbl"])
    violations["bbl"] = normalize_bbl(violations["bbl"])
    registrations["bbl"] = derive_bbl(registrations)

    complaints_before = len(complaints)
    violations_before = len(violations)

    complaints = complaints.dropna(subset=["bbl"])
    violations = violations.dropna(subset=["bbl"])
    registrations = registrations.dropna(subset=["bbl"])

    print(f"BBL normalization dropped {complaints_before - len(complaints):,} complaint rows")
    print(f"BBL normalization dropped {violations_before - len(violations):,} violation rows")
    print(f"  {len(registrations):,} registrations after BBL derivation")

    # --- Load ---
    print("Connecting to Neo4j...")
    driver = get_driver()

    print("Ensuring constraints...")
    ensure_constraints(driver)

    all_bbls = (
        list(complaints["bbl"])
        + list(violations["bbl"])
        + list(registrations["bbl"])
    )
    print("Loading Building nodes...")
    building_count = load_buildings(driver, all_bbls)
    print(f"  {building_count:,} Building nodes")

    print("Loading Complaint nodes and relationships...")
    c_nodes, c_rels = load_complaints(driver, complaints)
    print(f"  {c_nodes:,} Complaint nodes, {c_rels:,} FILED_AGAINST relationships")

    print("Loading Violation nodes and relationships...")
    v_nodes, v_rels = load_violations(driver, violations)
    print(f"  {v_nodes:,} Violation nodes, {v_rels:,} FILED_AGAINST relationships")

    print("Loading Registration nodes and relationships...")
    r_nodes, r_rels = load_registrations(driver, registrations)
    print(f"  {r_nodes:,} Registration nodes, {r_rels:,} REGISTERED_TO relationships")

    driver.close()
    print("Done.")


if __name__ == "__main__":
    run()

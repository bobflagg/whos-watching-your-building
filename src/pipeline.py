from src.graph.loader import (
    ensure_constraints,
    get_driver,
    load_agencies,
    load_building_addresses,
    load_buildings,
    load_complaints,
    load_contacts,
    load_dob_safety_violations,
    load_inspections,
    load_neighborhoods,
    load_registrations,
    load_violations,
)
from src.ingest.normalize import derive_bbl, normalize_bbl
from src.ingest.soda_client import fetch_all, fetch_all_paginated, fetch_recent_paginated, lookback_months

_311_DATASET = "erm2-nwe9"
_VIOLATIONS_DATASET = "wvxf-dwi5"
_REGISTRATIONS_DATASET = "tesw-yqqr"
_CONTACTS_DATASET = "feu5-w2e2"
_DOB_SAFETY_VIOLATIONS_DATASET = "855j-jady"


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

    print("Fetching HPD registration contacts (full pull, paginated)...")
    contacts = fetch_all_paginated(_CONTACTS_DATASET)
    print(f"  {len(contacts):,} contacts fetched")

    print("Fetching DOB Safety Violations (full pull, paginated)...")
    dob_violations = fetch_all_paginated(_DOB_SAFETY_VIOLATIONS_DATASET)
    print(f"  {len(dob_violations):,} DOB safety violations fetched")

    # --- Normalize BBL ---
    complaints["bbl"] = normalize_bbl(complaints["bbl"])
    violations["bbl"] = normalize_bbl(violations["bbl"])
    registrations["bbl"] = derive_bbl(registrations)
    dob_violations["bbl"] = normalize_bbl(dob_violations["bbl"])

    complaints_before = len(complaints)
    violations_before = len(violations)
    dob_violations_before = len(dob_violations)

    complaints = complaints.dropna(subset=["bbl"])
    violations = violations.dropna(subset=["bbl"])
    registrations = registrations.dropna(subset=["bbl"])
    dob_violations = dob_violations.dropna(subset=["bbl"])

    print(f"BBL normalization dropped {complaints_before - len(complaints):,} complaint rows")
    print(f"BBL normalization dropped {violations_before - len(violations):,} violation rows")
    print(f"BBL normalization dropped {dob_violations_before - len(dob_violations):,} DOB violation rows")
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
        + list(dob_violations["bbl"])
    )
    print("Loading Building nodes...")
    building_count = load_buildings(driver, all_bbls)
    print(f"  {building_count:,} Building nodes")

    print("Enriching Building nodes with address data...")
    load_building_addresses(driver, violations)
    load_building_addresses(driver, registrations)
    print("  Done")

    print("Loading Complaint nodes and relationships...")
    c_nodes, c_rels = load_complaints(driver, complaints)
    print(f"  {c_nodes:,} Complaint nodes, {c_rels:,} FILED_AGAINST relationships")

    print("Loading Agency nodes and relationships...")
    a_nodes, a_rels = load_agencies(driver, complaints)
    print(f"  {a_nodes:,} Agency nodes, {a_rels:,} HANDLED_BY relationships")

    print("Loading Violation nodes and relationships...")
    v_nodes, v_rels = load_violations(driver, violations)
    print(f"  {v_nodes:,} Violation nodes, {v_rels:,} HAS_VIOLATION relationships")

    print("Loading Inspection nodes and relationships...")
    i_nodes, i_rels = load_inspections(driver, violations)
    print(f"  {i_nodes:,} Inspection nodes, {i_rels:,} INSPECTED_BY relationships")

    print("Loading Neighborhood nodes and relationships...")
    n_nodes, n_rels = load_neighborhoods(driver, violations)
    print(f"  {n_nodes:,} Neighborhood nodes, {n_rels:,} LOCATED_IN relationships")

    print("Loading Registration nodes and relationships...")
    l_nodes, l_rels = load_registrations(driver, registrations)
    print(f"  {l_nodes:,} Registration nodes, {l_rels:,} OWNED_BY relationships")

    print("Loading Contact nodes and relationships...")
    ct_nodes, ct_rels = load_contacts(driver, contacts)
    print(f"  {ct_nodes:,} Contact nodes, {ct_rels:,} CONTACT_FOR relationships")

    print("Loading DOB Safety Violation nodes and relationships...")
    d_nodes, d_rels = load_dob_safety_violations(driver, dob_violations)
    print(f"  {d_nodes:,} DOBViolation nodes, {d_rels:,} HAS_DOB_VIOLATION relationships")

    driver.close()
    print("Done.")


if __name__ == "__main__":
    run()

import marimo

__generated_with = "0.23.2"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Phase 4 — Graph Loading: Validation

    Verifies that all node types, relationship types, BBL join coverage,
    and uniqueness constraints meet the acceptance criteria from
    `specs/2026-04-27-graph-loading/validation.md`.
    """)
    return


@app.cell
def _():
    import sys
    import pandas as pd
    sys.path.insert(0, "../")
    from src.graph.loader import get_driver, _DATABASE

    driver = get_driver()
    return driver, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Node Counts by Label

    All seven labels must have at least one node.
    """)
    return


@app.cell
def _(driver, pd):
    node_queries = [
        ("Building",     "MATCH (n:Building)     RETURN count(n) AS n"),
        ("Complaint",    "MATCH (n:Complaint)    RETURN count(n) AS n"),
        ("Violation",    "MATCH (n:Violation)    RETURN count(n) AS n"),
        ("Landlord",     "MATCH (n:Landlord)     RETURN count(n) AS n"),
        ("Agency",       "MATCH (n:Agency)       RETURN count(n) AS n"),
        ("Inspection",   "MATCH (n:Inspection)   RETURN count(n) AS n"),
        ("Neighborhood", "MATCH (n:Neighborhood) RETURN count(n) AS n"),
    ]
    node_counts = []
    with driver.session(database=_DATABASE) as session:
        for label, q in node_queries:
            count = session.run(q).single()["n"]
            node_counts.append({"label": label, "count": count, "pass": count > 0})

    pd.DataFrame(node_counts)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Relationship Counts by Type

    All six relationship types must have at least one instance with the correct direction.
    """)
    return


@app.cell
def _(driver, pd):
    rel_queries = [
        ("FILED_AGAINST",  "(Complaint)→(Building)",   "MATCH (:Complaint)-[r:FILED_AGAINST]->(:Building)   RETURN count(r) AS n"),
        ("HAS_VIOLATION",  "(Building)→(Violation)",   "MATCH (:Building)-[r:HAS_VIOLATION]->(:Violation)   RETURN count(r) AS n"),
        ("OWNED_BY",       "(Building)→(Landlord)",    "MATCH (:Building)-[r:OWNED_BY]->(:Landlord)         RETURN count(r) AS n"),
        ("LOCATED_IN",     "(Building)→(Neighborhood)","MATCH (:Building)-[r:LOCATED_IN]->(:Neighborhood)   RETURN count(r) AS n"),
        ("HANDLED_BY",     "(Complaint)→(Agency)",     "MATCH (:Complaint)-[r:HANDLED_BY]->(:Agency)        RETURN count(r) AS n"),
        ("INSPECTED_BY",   "(Violation)→(Inspection)", "MATCH (:Violation)-[r:INSPECTED_BY]->(:Inspection)  RETURN count(r) AS n"),
    ]
    rel_counts = []
    with driver.session(database=_DATABASE) as _session:
        for rel_type, direction, _q in rel_queries:
            _count = _session.run(_q).single()["n"]
            rel_counts.append({"type": rel_type, "direction": direction, "count": _count, "pass": _count > 0})

    pd.DataFrame(rel_counts)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Schema Correctness — Old Labels Must Not Exist

    Confirms that the Phase 2 labels were replaced, not duplicated.
    """)
    return


@app.cell
def _(driver, pd):
    stale_queries = [
        ("Registration nodes (must be 0)",  "MATCH (n:Registration) RETURN count(n) AS n"),
        ("REGISTERED_TO rels (must be 0)",  "MATCH ()-[r:REGISTERED_TO]->() RETURN count(r) AS n"),
        ("Violation→Building FILED_AGAINST (must be 0)",
         "MATCH (:Violation)-[r:FILED_AGAINST]->(:Building) RETURN count(r) AS n"),
    ]
    stale_counts = []
    with driver.session(database=_DATABASE) as _session:
        for _label, _q in stale_queries:
            _count = _session.run(_q).single()["n"]
            stale_counts.append({"check": _label, "count": _count, "pass": _count == 0})

    pd.DataFrame(stale_counts)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. BBL Join Coverage

    Pass threshold: ≥ 80% of Complaints and Violations linked to a Building node.
    """)
    return


@app.cell
def _(driver, pd):
    with driver.session(database=_DATABASE) as _session:
        total_complaints = _session.run("MATCH (n:Complaint) RETURN count(n) AS n").single()["n"]
        linked_complaints = _session.run(
            "MATCH (c:Complaint)-[:FILED_AGAINST]->(:Building) RETURN count(c) AS n"
        ).single()["n"]

        total_violations = _session.run("MATCH (n:Violation) RETURN count(n) AS n").single()["n"]
        linked_violations = _session.run(
            "MATCH (:Building)-[:HAS_VIOLATION]->(v:Violation) RETURN count(v) AS n"
        ).single()["n"]

        total_buildings = _session.run("MATCH (n:Building) RETURN count(n) AS n").single()["n"]
        owned_buildings = _session.run(
            "MATCH (b:Building)-[:OWNED_BY]->(:Landlord) RETURN count(DISTINCT b) AS n"
        ).single()["n"]

    c_pct = 100 * linked_complaints / total_complaints if total_complaints else 0
    v_pct = 100 * linked_violations / total_violations if total_violations else 0
    b_pct = 100 * owned_buildings / total_buildings if total_buildings else 0

    coverage_df = pd.DataFrame([
        {
            "metric": "Complaints with FILED_AGAINST",
            "linked": linked_complaints,
            "total": total_complaints,
            "pct": f"{c_pct:.1f}%",
            "pass": c_pct >= 80,
        },
        {
            "metric": "Violations with HAS_VIOLATION",
            "linked": linked_violations,
            "total": total_violations,
            "pct": f"{v_pct:.1f}%",
            "pass": v_pct >= 80,
        },
        {
            "metric": "Buildings with OWNED_BY",
            "linked": owned_buildings,
            "total": total_buildings,
            "pct": f"{b_pct:.1f}%",
            "pass": True,
        },
    ])
    coverage_df
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Uniqueness Constraints

    All seven constraints must be present.
    """)
    return


@app.cell
def _(driver, pd):
    with driver.session(database=_DATABASE) as _session:
        result = _session.run("SHOW CONSTRAINTS")
        constraints = [
            {"name": r["name"], "type": r["type"], "labelsOrTypes": r["labelsOrTypes"], "properties": r["properties"]}
            for r in result
        ]

    expected = {
        ("Building", "bbl"),
        ("Complaint", "complaint_id"),
        ("Violation", "violation_id"),
        ("Landlord", "registration_id"),
        ("Agency", "agency_code"),
        ("Inspection", "inspection_id"),
        ("Neighborhood", "ntacode"),
    }

    found = set()
    for c in constraints:
        labels = c.get("labelsOrTypes") or []
        props = c.get("properties") or []
        if labels and props:
            found.add((labels[0], props[0]))

    constraint_check = pd.DataFrame([
        {"label": lbl, "property": prop, "pass": (lbl, prop) in found}
        for lbl, prop in sorted(expected)
    ])
    constraint_check
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Sample Traversal

    Pick one BBL and show its connected Complaints, Violations, and Landlord.
    A non-empty result confirms the graph is navigable end-to-end.
    """)
    return


@app.cell
def _(driver, mo):
    with driver.session(database=_DATABASE) as _session:
        sample_bbl_result = _session.run(
            "MATCH (b:Building)-[:HAS_VIOLATION]->(:Violation) "
            "MATCH (b)-[:OWNED_BY]->(:Landlord) "
            "RETURN b.bbl AS bbl LIMIT 1"
        ).single()

    if sample_bbl_result is None:
        mo.md("**No BBL found with both violations and a landlord.**")
    else:
        sample_bbl = sample_bbl_result["bbl"]
        with driver.session(database=_DATABASE) as _session:
            record = _session.run(
                "MATCH (b:Building {bbl: $bbl}) "
                "OPTIONAL MATCH (c:Complaint)-[:FILED_AGAINST]->(b) "
                "OPTIONAL MATCH (b)-[:HAS_VIOLATION]->(v:Violation) "
                "OPTIONAL MATCH (b)-[:OWNED_BY]->(l:Landlord) "
                "OPTIONAL MATCH (b)-[:LOCATED_IN]->(n:Neighborhood) "
                "RETURN "
                "  b.bbl AS bbl, "
                "  count(DISTINCT c) AS complaints, "
                "  count(DISTINCT v) AS violations, "
                "  count(DISTINCT l) AS landlords, "
                "  collect(DISTINCT n.ntacode)[0] AS neighborhood",
                bbl=sample_bbl,
            ).single()

        mo.md(f"""
    **Sample BBL:** `{record['bbl']}`

    | Metric | Count |
    |---|---|
    | Complaints | {record['complaints']} |
    | Violations | {record['violations']} |
    | Landlord registrations | {record['landlords']} |
    | Neighborhood (NTA) | {record['neighborhood'] or 'n/a'} |
        """)
    return


@app.cell
def _():
    (
        "MATCH (b:Building {bbl: $bbl}) "
        "OPTIONAL MATCH (c:Complaint)-[:FILED_AGAINST]->(b) "
        "OPTIONAL MATCH (b)-[:HAS_VIOLATION]->(v:Violation) "
        "OPTIONAL MATCH (b)-[:OWNED_BY]->(l:Landlord) "
        "OPTIONAL MATCH (b)-[:LOCATED_IN]->(n:Neighborhood) "
        "RETURN "
        "  b.bbl AS bbl, "
        "  count(DISTINCT c) AS complaints, "
        "  count(DISTINCT v) AS violations, "
        "  count(DISTINCT l) AS landlords, "
        "  collect(DISTINCT n.ntacode)[0] AS neighborhood"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Idempotency Check

    Re-run the pipeline, then execute this cell. All counts should be identical to section 1.
    """)
    return


@app.cell
def _(driver, pd):
    rerun_queries = [
        ("Building",     "MATCH (n:Building)     RETURN count(n) AS n"),
        ("Complaint",    "MATCH (n:Complaint)    RETURN count(n) AS n"),
        ("Violation",    "MATCH (n:Violation)    RETURN count(n) AS n"),
        ("Landlord",     "MATCH (n:Landlord)     RETURN count(n) AS n"),
        ("Agency",       "MATCH (n:Agency)       RETURN count(n) AS n"),
        ("Inspection",   "MATCH (n:Inspection)   RETURN count(n) AS n"),
        ("Neighborhood", "MATCH (n:Neighborhood) RETURN count(n) AS n"),
    ]
    rerun_counts = []
    with driver.session(database=_DATABASE) as _session:
        for _label, _q in rerun_queries:
            _count = _session.run(_q).single()["n"]
            rerun_counts.append({"label": _label, "count": _count})

    pd.DataFrame(rerun_counts)
    return


if __name__ == "__main__":
    app.run()

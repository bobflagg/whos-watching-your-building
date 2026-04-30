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
    # Phase 5 — DOB Safety Violations: Validation

    Verifies that `DOBViolation` nodes and `HAS_DOB_VIOLATION` relationships are
    loaded correctly and meet the acceptance criteria from
    `specs/2026-04-30-phase-5-dob-safety-violations/validation.md`.
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
    ## 1. DOBViolation Constraint

    The uniqueness constraint on `violation_number` must be present in Neo4j.
    """)
    return


@app.cell
def _(driver, pd):
    with driver.session(database=_DATABASE) as _session:
        result = _session.run("SHOW CONSTRAINTS")
        constraints = [
            {"labelsOrTypes": r["labelsOrTypes"], "properties": r["properties"]}
            for r in result
        ]

    found = set()
    for _c in constraints:
        _labels = _c.get("labelsOrTypes") or []
        _props = _c.get("properties") or []
        if _labels and _props:
            found.add((_labels[0], _props[0]))

    dob_constraint_ok = ("DOBViolation", "violation_number") in found

    pd.DataFrame([{
        "label": "DOBViolation",
        "property": "violation_number",
        "pass": dob_constraint_ok,
    }])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Node and Relationship Counts

    `DOBViolation` node count and `HAS_DOB_VIOLATION` relationship count must both be > 0.
    """)
    return


@app.cell
def _(driver, pd):
    with driver.session(database=_DATABASE) as _session:
        dob_nodes = _session.run("MATCH (d:DOBViolation) RETURN count(d) AS n").single()["n"]
        dob_rels = _session.run(
            "MATCH (:Building)-[r:HAS_DOB_VIOLATION]->(:DOBViolation) RETURN count(r) AS n"
        ).single()["n"]

    pd.DataFrame([
        {"metric": "DOBViolation nodes",          "count": dob_nodes, "pass": dob_nodes > 0},
        {"metric": "HAS_DOB_VIOLATION relationships", "count": dob_rels,  "pass": dob_rels > 0},
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. BBL Match Rate

    Pass threshold: ≥ 50% of `DOBViolation` nodes linked to a Building via `HAS_DOB_VIOLATION`.

    DOB NOW is a newer system and may not have BBLs on all historical records,
    so the floor is lower than the 80% used for HPD data.
    """)
    return


@app.cell
def _(driver, pd):
    with driver.session(database=_DATABASE) as _session:
        _result = _session.run("""
            MATCH (d:DOBViolation)
            OPTIONAL MATCH (b:Building)-[:HAS_DOB_VIOLATION]->(d)
            RETURN
              count(d) AS total,
              count(b) AS linked
        """).single()

    _total = _result["total"]
    _linked = _result["linked"]
    _pct = 100 * _linked / _total if _total else 0

    pd.DataFrame([{
        "metric": "DOBViolations with HAS_DOB_VIOLATION",
        "linked": _linked,
        "total": _total,
        "pct": f"{_pct:.1f}%",
        "pass": _pct >= 50,
    }])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Cross-Dataset Coverage

    At least one Building must have both an HPD violation (`HAS_VIOLATION`) and a
    DOB violation (`HAS_DOB_VIOLATION`). Confirms the two enforcement datasets
    share BBL space and can be co-traversed.
    """)
    return


@app.cell
def _(driver, pd):
    with driver.session(database=_DATABASE) as _session:
        _both = _session.run("""
            MATCH (b:Building)-[:HAS_VIOLATION]->(:Violation)
            MATCH (b)-[:HAS_DOB_VIOLATION]->(:DOBViolation)
            RETURN count(DISTINCT b) AS n
        """).single()["n"]

    pd.DataFrame([{
        "metric": "Buildings with both HAS_VIOLATION and HAS_DOB_VIOLATION",
        "count": _both,
        "pass": _both > 0,
    }])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Sample Traversal

    Pick a building that has DOB violations and show HPD violations alongside DOB violations.
    A non-empty result confirms the graph is navigable across both enforcement datasets.
    """)
    return


@app.cell
def _(driver, mo):
    with driver.session(database=_DATABASE) as _session:
        _bbl_row = _session.run("""
            MATCH (b:Building)-[:HAS_DOB_VIOLATION]->(:DOBViolation)
            MATCH (b)-[:HAS_VIOLATION]->(:Violation)
            RETURN b.bbl AS bbl LIMIT 1
        """).single()

    if _bbl_row is None:
        mo.md("**No building found with both HPD and DOB violations.**")
    else:
        _bbl = _bbl_row["bbl"]
        with driver.session(database=_DATABASE) as _session:
            _record = _session.run("""
                MATCH (b:Building {bbl: $bbl})
                OPTIONAL MATCH (b)-[:HAS_VIOLATION]->(v:Violation)
                OPTIONAL MATCH (b)-[:HAS_DOB_VIOLATION]->(d:DOBViolation)
                OPTIONAL MATCH (l:Landlord)-[:OWNED_BY]->(b)
                RETURN
                  b.bbl              AS bbl,
                  b.house_number     AS house_number,
                  b.street_name      AS street_name,
                  b.borough          AS borough,
                  count(DISTINCT v)  AS hpd_violations,
                  count(DISTINCT d)  AS dob_violations,
                  count(DISTINCT l)  AS landlords
            """, bbl=_bbl).single()

        mo.md(f"""
    **Sample BBL:** `{_record['bbl']}`
    **Address:** {_record['house_number'] or '?'} {_record['street_name'] or '?'}, {_record['borough'] or '?'}

    | Metric | Count |
    |---|---|
    | HPD violations | {_record['hpd_violations']} |
    | DOB violations | {_record['dob_violations']} |
    | Landlord registrations | {_record['landlords']} |
        """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Device Type Distribution

    Informational — shows which safety equipment categories are represented.
    """)
    return


@app.cell
def _(driver, pd):
    with driver.session(database=_DATABASE) as _session:
        _rows = _session.run("""
            MATCH (d:DOBViolation)
            RETURN d.device_type AS device_type, count(d) AS count
            ORDER BY count DESC
        """)
        _device_data = [{"device_type": r["device_type"], "count": r["count"]} for r in _rows]

    pd.DataFrame(_device_data)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Violation Status Distribution

    Informational — shows the breakdown of active vs. resolved violations.
    """)
    return


@app.cell
def _(driver, pd):
    with driver.session(database=_DATABASE) as _session:
        _rows = _session.run("""
            MATCH (d:DOBViolation)
            RETURN d.violation_status AS violation_status, count(d) AS count
            ORDER BY count DESC
        """)
        _status_data = [{"violation_status": r["violation_status"], "count": r["count"]} for r in _rows]

    pd.DataFrame(_status_data)
    return


if __name__ == "__main__":
    app.run()

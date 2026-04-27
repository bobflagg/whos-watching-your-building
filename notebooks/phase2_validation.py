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
    # Phase 2 — Core Data Ingestion: Validation

    Confirms that the ingestion pipeline succeeded and quantifies join coverage across all three datasets.
    """)
    return


@app.cell
def _():
    import sys
    import pandas as pd
    sys.path.insert(0, "../")
    from src.ingest.soda_client import fetch_all, fetch_recent_paginated, lookback_months
    #from src.ingest.normalize import derive_bbl, normalize_bbl
    from src.ingest.normalize import normalize_bbl
    from src.graph.loader import get_driver

    return (
        fetch_all,
        fetch_recent_paginated,
        get_driver,
        lookback_months,
        normalize_bbl,
        pd,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Row Counts — Raw Fetch
    """)
    return


@app.cell
def _(fetch_all, fetch_recent_paginated, lookback_months, pd):
    months = lookback_months()
    print(f"Lookback window: {months} months")

    complaints_raw = fetch_recent_paginated("erm2-nwe9", "created_date", agency="HPD")
    violations_raw = fetch_recent_paginated("wvxf-dwi5", "inspectiondate")
    registrations_raw = fetch_all("tesw-yqqr")

    raw_counts = pd.DataFrame({
        "dataset": ["311 HPD Complaints", "HPD Violations", "HPD Registrations"],
        "raw_rows": [len(complaints_raw), len(violations_raw), len(registrations_raw)],
    })
    raw_counts
    return complaints_raw, registrations_raw, violations_raw


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. BBL Normalization — Drop Rates
    """)
    return


@app.cell
def _(complaints_raw, normalize_bbl, pd, registrations_raw, violations_raw):
    from src.ingest.normalize import derive_bbl

    complaints_norm = complaints_raw.copy()
    violations_norm = violations_raw.copy()
    registrations_norm = registrations_raw.copy()

    complaints_norm["bbl"] = normalize_bbl(complaints_norm["bbl"])
    violations_norm["bbl"] = normalize_bbl(violations_norm["bbl"])
    registrations_norm["bbl"] = derive_bbl(registrations_norm)

    def drop_stats(raw, normed, name):
        dropped = len(raw) - normed["bbl"].notna().sum()
        pct = 100 * dropped / len(raw) if len(raw) else 0
        return {"dataset": name, "raw_rows": len(raw), "bbl_nulls_dropped": int(dropped), "drop_pct": round(pct, 2)}

    bbl_stats = pd.DataFrame([
        drop_stats(complaints_raw, complaints_norm, "311 HPD Complaints"),
        drop_stats(violations_raw, violations_norm, "HPD Violations"),
        drop_stats(registrations_raw, registrations_norm, "HPD Registrations"),
    ])
    bbl_stats
    return complaints_norm, registrations_norm, violations_norm


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. BBL Format Sanity Check
    """)
    return


@app.cell
def _(complaints_norm, mo, registrations_norm, violations_norm):
    def format_check(series, name):
        clean = series.dropna()
        all_10 = (clean.str.len() == 10).all()
        all_numeric = clean.str.isnumeric().all()
        return f"**{name}:** len=10 → `{all_10}`, numeric → `{all_numeric}`, sample: `{clean.iloc[0] if len(clean) else 'n/a'}`"

    mo.md("\n\n".join([
        format_check(complaints_norm["bbl"], "311 Complaints"),
        format_check(violations_norm["bbl"], "HPD Violations"),
        format_check(registrations_norm["bbl"], "HPD Registrations"),
    ]))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Cross-Dataset BBL Join Coverage
    """)
    return


@app.cell
def _(complaints_norm, pd, registrations_norm, violations_norm):
    bbl_c = set(complaints_norm["bbl"].dropna())
    bbl_v = set(violations_norm["bbl"].dropna())
    bbl_r = set(registrations_norm["bbl"].dropna())

    all_bbls = bbl_c | bbl_v | bbl_r

    coverage = pd.DataFrame({
        "metric": [
            "Distinct BBLs — complaints",
            "Distinct BBLs — violations",
            "Distinct BBLs — registrations",
            "BBLs in all three datasets",
            "Complaint BBLs with a registration",
            "Violation BBLs with a registration",
            "Complaint BBL registration match rate",
            "Violation BBL registration match rate",
        ],
        "value": [
            len(bbl_c),
            len(bbl_v),
            len(bbl_r),
            len(bbl_c & bbl_v & bbl_r),
            len(bbl_c & bbl_r),
            len(bbl_v & bbl_r),
            f"{100 * len(bbl_c & bbl_r) / len(bbl_c):.1f}%" if bbl_c else "n/a",
            f"{100 * len(bbl_v & bbl_r) / len(bbl_v):.1f}%" if bbl_v else "n/a",
        ],
    })
    coverage
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Neo4j Node and Relationship Counts
    """)
    return


@app.cell
def _(get_driver, pd):
    driver = get_driver()
    queries = [
        ("Building nodes",     "MATCH (n:Building) RETURN count(n) AS n"),
        ("Complaint nodes",    "MATCH (n:Complaint) RETURN count(n) AS n"),
        ("Violation nodes",    "MATCH (n:Violation) RETURN count(n) AS n"),
        ("Registration nodes", "MATCH (n:Registration) RETURN count(n) AS n"),
        ("FILED_AGAINST rels", "MATCH ()-[r:FILED_AGAINST]->() RETURN count(r) AS n"),
        ("REGISTERED_TO rels", "MATCH ()-[r:REGISTERED_TO]->() RETURN count(r) AS n"),
    ]
    neo4j_counts = []
    with driver.session() as session:
        for label, query in queries:
            result = session.run(query)
            neo4j_counts.append({"label": label, "count": result.single()["n"]})
    driver.close()

    pd.DataFrame(neo4j_counts)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Idempotency Check

    Run the cell below **after** running the pipeline a second time.
    Counts should be unchanged from the table above.
    """)
    return


@app.cell
def _(get_driver, pd):
    driver2 = get_driver()
    queries2 = [
        ("Building nodes",     "MATCH (n:Building) RETURN count(n) AS n"),
        ("Complaint nodes",    "MATCH (n:Complaint) RETURN count(n) AS n"),
        ("Violation nodes",    "MATCH (n:Violation) RETURN count(n) AS n"),
        ("Registration nodes", "MATCH (n:Registration) RETURN count(n) AS n"),
    ]
    rerun_counts = []
    with driver2.session() as _session:
        for _label, _query in queries2:
            _result = _session.run(_query)
            rerun_counts.append({"label": _label, "count": _result.single()["n"]})
    driver2.close()

    pd.DataFrame(rerun_counts)
    return


if __name__ == "__main__":
    app.run()

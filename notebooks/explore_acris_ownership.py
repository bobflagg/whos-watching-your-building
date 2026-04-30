import marimo

__generated_with = "0.23.2"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # ACRIS Ownership — Schema Exploration (Phase 6)

    ACRIS (Automated City Register Information System) tracks every deed transfer and
    mortgage recording in NYC. Three datasets join on `document_id`:

    | Dataset | ID | Contents |
    |---|---|---|
    | Real Property Master | `7isb-wh4c` | Document metadata: `doc_type`, dates, amount |
    | Real Property Legals | `8h5j-fqxa` | BBL info: `borough`, `block`, `lot` per document |
    | Real Property Parties | `636b-3b5g` | Buyer/seller names per document |

    Goals:
    1. Identify which `doc_type` values correspond to deed transfers
    2. Confirm BBL construction from borough/block/lot matches our existing graph format
    3. Understand party name variation and normalization needs
    4. Find a known multi-building LLC to use as validation anchor
    """)
    return


@app.cell
def _():
    import sys
    import pandas as pd
    sys.path.insert(0, "..")
    from src.ingest.soda_client import fetch_sample

    MASTER_ID  = "7isb-wh4c"
    LEGALS_ID  = "8h5j-fqxa"
    PARTIES_ID = "636b-3b5g"
    SAMPLE     = 2_000
    return LEGALS_ID, MASTER_ID, PARTIES_ID, SAMPLE, fetch_sample, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 1. ACRIS Master — doc_type inventory
    """)
    return


@app.cell
def _(MASTER_ID, SAMPLE, fetch_sample):
    df_master = fetch_sample(MASTER_ID, limit=SAMPLE)
    print(f"Master sample: {len(df_master):,} rows, {len(df_master.columns)} columns")
    return (df_master,)


@app.cell
def _(df_master, pd):
    schema_master = pd.DataFrame({
        "dtype":      df_master.dtypes,
        "null_pct":   (df_master.isna().mean() * 100).round(1),
        "sample":     [df_master[c].dropna().iloc[0] if df_master[c].notna().any() else None
                       for c in df_master.columns],
    })
    schema_master
    return


@app.cell
def _(df_master):
    doc_type_counts = df_master["doc_type"].value_counts().rename_axis("doc_type").reset_index(name="count")
    doc_type_counts.head(40)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Deed doc_type values

    From the counts above, identify all deed-transfer doc types (typically anything containing
    "DEED"). These will be the filter for ingestion.
    """)
    return


@app.cell
def _(df_master):
    deed_types = df_master[df_master["doc_type"].str.contains("DEED", na=False)]["doc_type"].value_counts()
    print("Deed-related doc_types found in sample:")
    print(deed_types.to_string())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 2. ACRIS Legals — BBL construction
    """)
    return


@app.cell
def _(LEGALS_ID, SAMPLE, fetch_sample):
    df_legals = fetch_sample(LEGALS_ID, limit=SAMPLE)
    print(f"Legals sample: {len(df_legals):,} rows, {len(df_legals.columns)} columns")
    return (df_legals,)


@app.cell
def _(df_legals, pd):
    schema_legals = pd.DataFrame({
        "dtype":    df_legals.dtypes,
        "null_pct": (df_legals.isna().mean() * 100).round(1),
        "sample":   [df_legals[c].dropna().iloc[0] if df_legals[c].notna().any() else None
                     for c in df_legals.columns],
    })
    schema_legals
    return


@app.cell
def _(df_legals):
    bbl_cols = [c for c in df_legals.columns if any(x in c.lower() for x in ("borough", "block", "lot", "bbl"))]
    print("BBL-related columns:", bbl_cols)
    df_legals[bbl_cols].head(10)
    return


@app.cell
def _(df_legals):
    df_legals["borough"].value_counts().sort_index()
    return


@app.cell
def _(df_legals):
    sample_bbl = (
        df_legals["borough"].astype(str).str.strip().str.zfill(1)
        + df_legals["block"].astype(str).str.strip().str.zfill(5)
        + df_legals["lot"].astype(str).str.strip().str.zfill(4)
    )
    valid_bbl = sample_bbl[sample_bbl.str.len() == 10]
    print(f"Valid 10-char BBLs: {len(valid_bbl):,} / {len(df_legals):,}")
    print("Sample BBLs:", valid_bbl.head(5).tolist())
    return (sample_bbl,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Spot-check: do constructed BBLs overlap with Building nodes in our graph?
    """)
    return


@app.cell
def _(sample_bbl):
    import os
    from dotenv import load_dotenv
    from neo4j import GraphDatabase

    load_dotenv()

    driver = GraphDatabase.driver(
        os.environ["NEO4J_URI"],
        auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"]),
    )

    test_bbls = sample_bbl[sample_bbl.str.len() == 10].head(20).tolist()

    with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
        result = session.run(
            "UNWIND $bbls AS bbl MATCH (b:Building {bbl: bbl}) RETURN bbl",
            bbls=test_bbls,
        )
        matched = [r["bbl"] for r in result]

    print(f"Tested {len(test_bbls)} BBLs from ACRIS Legals sample")
    print(f"Matched {len(matched)} in our Building graph")
    print("Matched BBLs:", matched[:5])
    driver.close()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 3. ACRIS Parties — name formats and normalization
    """)
    return


@app.cell
def _(PARTIES_ID, SAMPLE, fetch_sample):
    df_parties = fetch_sample(PARTIES_ID, limit=SAMPLE)
    print(f"Parties sample: {len(df_parties):,} rows, {len(df_parties.columns)} columns")
    return (df_parties,)


@app.cell
def _(df_parties, pd):
    schema_parties = pd.DataFrame({
        "dtype":    df_parties.dtypes,
        "null_pct": (df_parties.isna().mean() * 100).round(1),
        "sample":   [df_parties[c].dropna().iloc[0] if df_parties[c].notna().any() else None
                     for c in df_parties.columns],
    })
    schema_parties
    return


@app.cell
def _(df_parties):
    df_parties["party_type"].value_counts()
    return


@app.cell
def _(df_parties):
    buyers  = df_parties[df_parties["party_type"] == "1"]["name"].dropna()
    sellers = df_parties[df_parties["party_type"] == "2"]["name"].dropna()
    print(f"Buyer names (party_type=1): {len(buyers):,}")
    print(f"Seller names (party_type=2): {len(sellers):,}")
    print("\nSample buyer names:")
    print(buyers.head(20).tolist())
    return


@app.cell
def _(df_parties):
    llc_names = df_parties[df_parties["name"].str.contains(r"LLC|L\.L\.C|CORP|INC|TRUST", na=False, case=False)]["name"].dropna()
    print(f"Entity-style names in sample: {len(llc_names):,}")
    print("\nSample entity names:")
    print(llc_names.head(30).tolist())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Name normalization assessment

    Look at the entity names above for:
    - Mixed case vs uppercase: is the data consistently uppercase?
    - LLC punctuation variants: `LLC` vs `L.L.C.` vs `L L C`
    - Trailing/leading whitespace
    - Suffix patterns to handle: LLC, L.L.C, INC, CORP, CO, TRUST, ASSOC, etc.
    """)
    return


@app.cell
def _(df_parties):
    import re

    all_names = df_parties["name"].dropna().astype(str)

    lower_count = all_names[all_names.str.lower() == all_names].sum() if False else (all_names != all_names.str.upper()).sum()
    has_leading_space = all_names.str.startswith(" ").sum()
    has_trailing_space = all_names.str.endswith(" ").sum()
    has_double_space = all_names.str.contains(r"  ").sum()

    print(f"Names not all-uppercase: {lower_count:,}")
    print(f"Names with leading space: {has_leading_space:,}")
    print(f"Names with trailing space: {has_trailing_space:,}")
    print(f"Names with double space: {has_double_space:,}")

    llc_variants = all_names[all_names.str.contains(r"L\.?L\.?C\.?", na=False)]
    print(f"\nLLC variant forms ({len(llc_variants)} total):")
    print(llc_variants.value_counts().head(20).to_string())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 4. Joined sample — deed parties with BBL
    """)
    return


@app.cell
def _(LEGALS_ID, MASTER_ID, PARTIES_ID, fetch_sample):
    deed_master = fetch_sample(MASTER_ID, limit=500)
    deed_master = deed_master[deed_master["doc_type"].str.contains("DEED", na=False)]
    deed_ids = deed_master["document_id"].tolist()
    print(f"Deed documents in master sample: {len(deed_ids)}")

    all_legals = fetch_sample(LEGALS_ID, limit=2_000)
    all_parties = fetch_sample(PARTIES_ID, limit=2_000)

    legals_filtered = all_legals[all_legals["document_id"].isin(deed_ids)].copy()
    parties_filtered = all_parties[all_parties["document_id"].isin(deed_ids)].copy()

    legals_filtered["bbl"] = (
        legals_filtered["borough"].astype(str).str.strip().str.zfill(1)
        + legals_filtered["block"].astype(str).str.strip().str.zfill(5)
        + legals_filtered["lot"].astype(str).str.strip().str.zfill(4)
    )

    joined = parties_filtered.merge(legals_filtered[["document_id", "bbl"]], on="document_id", how="left")
    joined = joined.merge(deed_master[["document_id", "doc_type", "document_date"]], on="document_id", how="left")

    print(f"Joined deed-party records: {len(joined)}")
    joined[["document_id", "doc_type", "document_date", "party_type", "name", "bbl"]].head(20)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 5. Multi-building landlord candidates (validation anchor)
    """)
    return


@app.cell
def _(df_parties):
    entity_names = df_parties[
        df_parties["party_type"] == "1"
    ]["name"].dropna()

    entity_counts = entity_names.value_counts().reset_index()
    entity_counts.columns = ["name", "deed_count"]

    entities_only = entity_counts[
        entity_counts["name"].str.contains(r"LLC|L\.L\.C|CORP|INC|REALTY|HOLDINGS|PROPERTIES|MGMT|MANAGEMENT", na=False, case=False)
    ]

    print("Top entity buyers by deed count in this sample:")
    print(entities_only.head(20).to_string(index=False))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Validation anchor selection

    From the list above, choose a specific LLC or entity name that:
    1. Appears as a buyer on multiple deeds
    2. Is likely associated with problem properties (cross-check with HPD data)
    3. Has a distinctive enough name to use as a stable test case

    Record the chosen name in `specs/2026-04-30-acris-ownership-ingestion/exploration-notes.md`.
    """)
    return


if __name__ == "__main__":
    app.run()

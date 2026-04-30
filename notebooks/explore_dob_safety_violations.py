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
    # DOB Safety Violations — Schema Exploration
    **Dataset:** DOB Safety Violations (`855j-jady`)

    Violations issued through DOB NOW (the current DOB system). Covers boilers,
    elevators, gas piping, facades, benchmarking, structurally compromised buildings,
    and more. Updated near-real-time; excludes legacy BIS violations and OATH summonses.

    Full pull (no date filter) — captures all ~1.09M records, not just recent issues.
    """)
    return


@app.cell
def _():
    import sys
    #import marimo as mo
    import pandas as pd
    sys.path.insert(0, "..")
    from src.ingest.soda_client import fetch_all_paginated

    return fetch_all_paginated, pd


@app.cell
def _(fetch_all_paginated):
    df = fetch_all_paginated("855j-jady")
    print(f"Pulled {len(df):,} rows, {len(df.columns)} columns")
    return (df,)


@app.cell
def _(df):
    import pathlib
    out = pathlib.Path("../data/raw/dob_safety_violations.parquet")
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)
    print(f"Saved → {out}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Schema
    """)
    return


@app.cell
def _(df, pd):
    schema = pd.DataFrame({
        "dtype": df.dtypes,
        "null_count": df.isna().sum(),
        "null_pct": (df.isna().mean() * 100).round(1),
        "sample": [df[c].dropna().iloc[0] if df[c].notna().any() else None for c in df.columns],
    })
    schema
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## BBL Coverage
    """)
    return


@app.cell
def _(df, mo):
    bbl_col = "bbl" if "bbl" in df.columns else None
    if bbl_col:
        non_null = df[bbl_col].notna().sum()
        total = len(df)
        message = f"**BBL field:** `{bbl_col}` — {non_null:,} / {total:,} non-null ({100*non_null/total:.1f}%)"
    else:
        message = "**BBL field:** not found — check column names above"
    mo.md(message)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Device Type Distribution
    """)
    return


@app.cell
def _(df):
    df["device_type"].value_counts()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Violation Status Distribution
    """)
    return


@app.cell
def _(df):
    df["violation_status"].value_counts()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Sample Rows
    """)
    return


@app.cell
def _(df):
    df.head(5)
    return


if __name__ == "__main__":
    app.run()

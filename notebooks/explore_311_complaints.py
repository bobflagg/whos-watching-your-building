import marimo

__generated_with = "0.23.2"
app = marimo.App(width="full", title="311 HPD Complaints — Schema Exploration")


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # 311 HPD Complaints — Schema Exploration
    **Dataset:** 311 Service Requests (`erm2-nwe9`), filtered to `agency='HPD'`

    Pulls the last `LOOKBACK_MONTHS` months, saves to `data/raw/`, and documents
    schema, null rates, and BBL coverage for Phase 2 join planning.
    """)
    return


@app.cell
def _():
    import sys
    import marimo as mo
    import pandas as pd
    sys.path.insert(0, "..")
    from src.ingest.soda_client import fetch_recent, cutoff_date, lookback_months
    return cutoff_date, fetch_recent, lookback_months, mo, pd, sys


@app.cell
def _(cutoff_date, lookback_months, mo):
    mo.md(f"**Lookback window:** {lookback_months()} months (cutoff: {cutoff_date().strftime('%Y-%m-%d')})")
    return


@app.cell
def _(fetch_recent):
    df = fetch_recent("erm2-nwe9", "created_date", agency="HPD")
    print(f"Pulled {len(df):,} rows, {len(df.columns)} columns")
    return (df,)


@app.cell
def _(df):
    import pathlib
    out = pathlib.Path("../data/raw/311_hpd_complaints.parquet")
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)
    print(f"Saved → {out}")
    return (out,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("## Schema")
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
    return (schema,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("## BBL Coverage")
    return


@app.cell
def _(df, mo):
    bbl_col = "bbl" if "bbl" in df.columns else None
    if bbl_col:
        non_null = df[bbl_col].notna().sum()
        total = len(df)
        mo.md(f"**BBL field:** `{bbl_col}` — {non_null:,} / {total:,} non-null ({100*non_null/total:.1f}%)")
    else:
        mo.md("**BBL field:** not found — check column names above")
    return (bbl_col,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("## Sample Rows")
    return


@app.cell
def _(df):
    df.head(5)
    return


if __name__ == "__main__":
    app.run()

import marimo

__generated_with = "0.23.2"
app = marimo.App(width="full", title="HPD Registrations — Schema Exploration")


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # HPD Registrations — Schema Exploration
    **Dataset:** HPD Property Registrations (`tesw-yqqr`)

    Pulls the last `LOOKBACK_MONTHS` months using `lastmodifieddate` as the date filter,
    saves to `data/raw/`, and documents schema, null rates, and BBL coverage.

    > **Note:** Registrations represent property ownership records rather than events.
    > `lastregistrationdate` captures buildings re-registered recently. Alternative: `registrationenddate`.
    > Confirm the right field for Phase 2 ingestion strategy.
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
    df = fetch_recent("tesw-yqqr", "lastregistrationdate")
    print(f"Pulled {len(df):,} rows, {len(df.columns)} columns")
    return (df,)


@app.cell
def _(df):
    import pathlib
    out = pathlib.Path("../data/raw/hpd_registrations.parquet")
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

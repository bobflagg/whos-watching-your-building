import pandas as pd


def normalize_bbl(series: pd.Series) -> pd.Series:
    """Normalize an existing BBL column to a clean 10-character string.

    Strips whitespace and zero-pads to 10 chars. Returns NaN for values that
    are null or cannot be coerced to a 10-digit string.
    """
    result = series.astype(str).str.strip()
    result = result.str.replace(r"\D", "", regex=True)  # remove any non-digits
    result = result.str.zfill(10)
    result = result.where(result.str.len() == 10)  # null out malformed values
    result = result.where(series.notna())           # preserve original nulls as NaN
    return result


def derive_bbl(df: pd.DataFrame) -> pd.Series:
    """Construct a 10-character BBL from boroid, block, and lot columns.

    Used for the HPD registrations dataset which has no direct bbl field.
    """
    return (
        df["boroid"].astype(str).str.strip().str.zfill(1)
        + df["block"].astype(str).str.strip().str.zfill(5)
        + df["lot"].astype(str).str.strip().str.zfill(4)
    )

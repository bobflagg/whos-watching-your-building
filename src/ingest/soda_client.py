import os
from datetime import datetime, timedelta

import pandas as pd
from dotenv import load_dotenv
from sodapy import Socrata

load_dotenv()

_DOMAIN = "data.cityofnewyork.us"
_APP_TOKEN = os.getenv("NYC_OPEN_DATA_APP_TOKEN")
_LOOKBACK_MONTHS = int(os.getenv("LOOKBACK_MONTHS", "6"))


def lookback_months() -> int:
    return _LOOKBACK_MONTHS


def cutoff_date() -> datetime:
    return datetime.now() - timedelta(days=30 * _LOOKBACK_MONTHS)


def fetch_all(dataset_id: str) -> pd.DataFrame:
    """Fetch all records from a dataset with no date filter."""
    client = Socrata(_DOMAIN, app_token=_APP_TOKEN, timeout=60)
    try:
        records = client.get(dataset_id, limit=500_000)
    finally:
        client.close()
    return pd.DataFrame.from_records(records)


def fetch_recent(dataset_id: str, date_field: str, **filters) -> pd.DataFrame:
    """Fetch records newer than the LOOKBACK_MONTHS cutoff.

    Extra keyword args are added as equality filters, e.g. agency='HPD'.
    """
    cutoff = cutoff_date().strftime("%Y-%m-%dT%H:%M:%S")
    clauses = [f"{date_field} >= '{cutoff}'"]
    for field, value in filters.items():
        clauses.append(f"{field}='{value}'")

    client = Socrata(_DOMAIN, app_token=_APP_TOKEN, timeout=60)
    try:
        records = client.get(dataset_id, where=" AND ".join(clauses), limit=500_000)
    finally:
        client.close()

    return pd.DataFrame.from_records(records)


def fetch_recent_paginated(
    dataset_id: str,
    date_field: str,
    page_size: int = 50_000,
    **filters,
) -> pd.DataFrame:
    """Fetch all records newer than the LOOKBACK_MONTHS cutoff, paginating past the 500k cap.

    Uses $offset to page through results until a page returns fewer rows than page_size.
    Extra keyword args are added as equality filters, e.g. agency='HPD'.
    """
    cutoff = cutoff_date().strftime("%Y-%m-%dT%H:%M:%S")
    clauses = [f"{date_field} >= '{cutoff}'"]
    for field, value in filters.items():
        clauses.append(f"{field}='{value}'")
    where = " AND ".join(clauses)

    client = Socrata(_DOMAIN, app_token=_APP_TOKEN, timeout=60)
    all_records = []
    offset = 0
    try:
        while True:
            page = client.get(dataset_id, where=where, limit=page_size, offset=offset)
            all_records.extend(page)
            if len(page) < page_size:
                break
            offset += page_size
    finally:
        client.close()

    return pd.DataFrame.from_records(all_records)

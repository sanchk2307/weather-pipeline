from datetime import timedelta


def get_date_ranges(start_date, end_date, existing_dates):
    """
    Compute the date ranges that need to be fetched, excluding already-loaded dates.

    Splits the start_date to end_date window into contiguous ranges that
    exclude any dates present in existing_dates, enabling idempotent backfills.

    Args:
        start_date: datetime.date representing the start of the desired range.
        end_date: datetime.date representing the end of the desired range.
        existing_dates: List of datetime.date objects already present in BigQuery.

    Returns:
        List of (start, end) tuples of datetime.date, each representing a
        contiguous range of missing dates to fetch.
    """
    date_ranges = []
    existing_dates = sorted(d for d in existing_dates if start_date <= d <= end_date)
    left = start_date - timedelta(days=1)
    for right in existing_dates:
        if left + timedelta(days=1) <= right - timedelta(days=1):
            date_ranges.append((left + timedelta(days=1), right - timedelta(days=1)))
        left = right
    if left + timedelta(days=1) <= end_date:
        date_ranges.append((left + timedelta(days=1), end_date))
    return date_ranges


# Testing get_date_ranges
if __name__ == "__main__":
    from datetime import datetime

    existing_dates = [
        datetime(2025, 1, 1).date(),
        datetime(2025, 1, 2).date(),
        datetime(2025, 1, 3).date(),
        datetime(2025, 1, 4).date(),
        datetime(2025, 1, 5).date(),
        datetime(2025, 1, 6).date(),
        datetime(2025, 1, 7).date(),
        datetime(2025, 1, 8).date(),
        datetime(2025, 1, 9).date(),
        datetime(2025, 1, 10).date(),
    ]
    start_date = datetime(2025, 1, 1).date()
    end_date = datetime(2025, 1, 10).date()
    print(get_date_ranges(start_date, end_date, existing_dates))

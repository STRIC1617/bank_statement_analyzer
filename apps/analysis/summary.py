# apps/analysis/summary.py

import pandas as pd
from dateutil import parser


def summary(df: pd.DataFrame):
    print(df)
    """
    Calculate total transactions and duration of the statement in months.

    Args:
        df (DataFrame): The parsed transaction data.

    Returns:
        total_transactions (int): Number of rows in the statement.
        num_months (int): Duration in months from first to last transaction.
        (Optional) Additional info can be added.
    """
    if df.empty:
        return 0, 0

    try:
        # Try parsing the earliest and latest transaction dates
        
        dates = pd.to_datetime(df['Transaction Date'], errors='coerce', dayfirst=True)
        print(dates)
        valid_dates = dates.dropna()

        if valid_dates.empty:
            return len(df), 0

        min_date = valid_dates.min()
        max_date = valid_dates.max()

        # Calculate difference in months
        duration_days = (max_date - min_date).days
        num_months = max(1, duration_days // 30)

        return len(df), num_months

    except Exception as e:
        print(f"[summary] Error: {e}")
        return len(df), 0

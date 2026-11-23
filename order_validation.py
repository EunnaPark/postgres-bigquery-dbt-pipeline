import pandas as pd


def normalize_status(status: pd.Series) -> pd.Series:
    """Trim surrounding spaces and lowercase each order status.

    " COMPLETED " becomes "completed". Spaces inside a value are kept,
    and an empty status stays empty so the status check can reject it.
    """
    return status.str.strip().str.lower()

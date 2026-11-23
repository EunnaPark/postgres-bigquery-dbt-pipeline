import pandas as pd


def normalize_status(status: pd.Series) -> pd.Series:
    """Trim surrounding spaces and lowercase each order status.

    " COMPLETED " becomes "completed". Spaces inside a value are kept,
    and an empty status stays empty so the status check can reject it.
    """
    return status.str.strip().str.lower()
    

def is_valid_status(status: pd.Series) -> pd.Series:
    """Return True for each status that is an allowed order status.

    Allowed values are pending, completed, cancelled and refunded. The check
    is exact, so pass statuses through normalize_status first: " Completed "
    and an empty status both return False.
    """
    allowed_statuses = ["pending", "completed", "cancelled", "refunded"]
    return status.isin(allowed_statuses)

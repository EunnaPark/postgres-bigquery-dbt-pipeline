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

def is_negative_amount(amount: pd.Series) -> pd.Series:
    """Return True for each amount that is below zero.

    Zero and positive amounts return False. Amounts that failed to parse
    (NaN) also return False; the "Invalid amount" check rejects those.
    """
    return amount < 0


def is_zero_completed_amount(status: pd.Series, amount: pd.Series) -> pd.Series:
    """Return True for each order that is completed but has an amount of zero.

    A completed order must have a positive amount. Pending, cancelled and
    refunded orders with a zero amount return False, and so do completed
    orders with a positive amount. Pass statuses through normalize_status first.
    """

    zero_completed_amount = (
        status.eq("completed")
        & amount.eq(0)
    )
    return zero_completed_amount

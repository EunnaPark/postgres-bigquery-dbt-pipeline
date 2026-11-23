import pandas as pd

from order_validation import normalize_status


def test_trims_and_lowercases_status():
    status = pd.Series([" COMPLETED ", "Pending", "cancelled  "])

    result = normalize_status(status)

    assert result.tolist() == ["completed", "pending", "cancelled"]


def test_keeps_already_clean_status():
    status = pd.Series(["refunded"])

    assert normalize_status(status).tolist() == ["refunded"]


def test_keeps_empty_status_empty():
    # An empty status must stay "" so the status check rejects it.
    status = pd.Series(["", "   "])

    assert normalize_status(status).tolist() == ["", ""]


def test_keeps_inner_spaces():
    # Only surrounding spaces are removed; "on hold" is not a valid status
    # and should reach the status check unchanged.
    status = pd.Series([" On Hold "])

    assert normalize_status(status).tolist() == ["on hold"]

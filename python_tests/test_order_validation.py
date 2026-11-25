import pandas as pd

from order_validation import normalize_status, is_valid_status,is_negative_amount, is_zero_completed_amount


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

def test_valid_status():
    status = pd.Series(["pending", "completed", "cancelled", "refunded"])
    assert is_valid_status(status).tolist() == [True, True, True, True]
    

def test_invalid_status():
    status = pd.Series(["!!!!"])
    assert is_valid_status(status).tolist() == [False]
    

def test_empty_status():
    status = pd.Series([""])
    assert is_valid_status(status).tolist() == [False]


def test_negative_amount():
    amount = pd.Series([-1.0, 0.0, 5.0, float("nan")])
    assert is_negative_amount(amount).tolist() == [True, False, False, False]


def test_is_zero_completed_amount():
    status = pd.Series(["completed", "pending", "completed"])
    amount = pd.Series([0.0,          0.0,       5.0])
    assert is_zero_completed_amount(status, amount).tolist() == [True, False, False]
    
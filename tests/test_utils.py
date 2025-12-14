from datetime import date

import pytest

from app.schemas.common import Settings
from app.services.utils import compute_status, ensure_valid_date


def make_settings(target: int = 2000, tolerance: int = 200) -> Settings:
    return Settings(
        calorie_target=target,
        calorie_tolerance=tolerance,
        macro_mode="grams",
        protein_target=150,
        fat_target=60,
        carbs_target=200,
    )


def test_compute_status_under():
    settings = make_settings()
    assert compute_status(1500, settings) == "under"


def test_compute_status_ok():
    settings = make_settings()
    assert compute_status(2100, settings) == "ok"


def test_compute_status_over():
    settings = make_settings()
    assert compute_status(2500, settings) == "over"


def test_ensure_valid_date_success():
    result = ensure_valid_date("2024-05-01")
    assert result == date(2024, 5, 1)


def test_ensure_valid_date_failure():
    with pytest.raises(ValueError):
        ensure_valid_date("05/01/2024")

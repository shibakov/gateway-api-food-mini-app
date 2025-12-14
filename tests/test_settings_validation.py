import pytest
from pydantic import ValidationError

from app.schemas.common import Settings


def test_settings_macro_percent_sum_validation():
    with pytest.raises(ValidationError):
        Settings(
            calorie_target=2000,
            calorie_tolerance=200,
            macro_mode="percent",
            protein_target=40,
            fat_target=30,
            carbs_target=20,
        )


def test_settings_step_validation():
    with pytest.raises(ValidationError):
        Settings(
            calorie_target=2010,
            calorie_tolerance=200,
            macro_mode="grams",
            protein_target=150,
            fat_target=60,
            carbs_target=200,
        )

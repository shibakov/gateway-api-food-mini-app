from __future__ import annotations

from datetime import date, time
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator



class MealType(str, Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    snack = "snack"


class InsightSeverity(str, Enum):
    positive = "positive"
    neutral = "neutral"
    warning = "warning"


class Insight(BaseModel):
    text: str
    severity: InsightSeverity


class NutritionTotals(BaseModel):
    calories: int
    protein: float
    fat: float
    carbs: float


class Summary(NutritionTotals):
    status: Literal["under", "ok", "over"]


class MealSummary(NutritionTotals):
    meal_id: str
    meal_type: MealType
    meal_time: time
    items_count: int


class MealItem(BaseModel):
    item_id: str
    name: str
    grams: int
    calories: int
    protein: int
    fat: int
    carbs: int
    added_via: str | None = None


class DayResponse(BaseModel):
    date: date
    summary: Summary
    meals: list[MealSummary]
    insight: Insight | None = Field(default=None, description="Optional insight object")


class StatsDay(BaseModel):
    date: date
    calories: int
    protein: float
    fat: float
    carbs: float
    status: Literal["under", "ok", "over"]


class Settings(BaseModel):
    calorie_target: int
    calorie_tolerance: int
    macro_mode: Literal["percent", "grams"]
    protein_target: int
    fat_target: int
    carbs_target: int

    @field_validator("calorie_target", "calorie_tolerance")
    def validate_calorie_steps(cls, value: int) -> int:
        if value % 50 != 0:
            raise ValueError("Calorie target and tolerance must be multiples of 50")
        return value

    @field_validator("protein_target", "fat_target", "carbs_target")
    def validate_macro_steps(cls, value: int) -> int:
        if value % 5 != 0:
            raise ValueError("Macro targets must be multiples of 5")
        return value

    @model_validator(mode="after")
    def validate_macro_sum(cls, values: Settings) -> Settings:
        if values.macro_mode == "percent":
            total = values.protein_target + values.fat_target + values.carbs_target
            if total != 100:
                raise ValueError("Macro targets must sum to 100 when macro_mode=percent")
        return values



class MealRequest(BaseModel):
    date: date
    meal_type: MealType
    meal_time: time


class MealItemRequest(BaseModel):
    product_id: str
    grams: int
    added_via: str | None = None

    @field_validator("grams")
    def validate_grams(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("grams must be greater than 0")
        return value


class MealItemUpdateRequest(BaseModel):
    grams: int

    @field_validator("grams")
    def validate_grams(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("grams must be greater than 0")
        return value


class ProductRequest(BaseModel):
    name: str
    brand: str | None = None
    nutrition_per_100g: NutritionTotals


class ProductSearchResult(BaseModel):
    product_id: str
    name: str
    brand: str | None = None
    nutrition_per_100g: NutritionTotals


class ProductNutritionUpdate(BaseModel):
    nutrition_per_100g: NutritionTotals


class PhotoRecognitionResponse(BaseModel):
    status: Literal["not_implemented"]
    results: list[dict] = Field(default_factory=list)


class StatsResponse(BaseModel):
    range: Literal["7d", "14d", "30d"]
    items: list[StatsDay]

from __future__ import annotations

from fastapi import APIRouter, Depends

from ..dependencies import get_db_connection, get_user_id
from ..errors import NotFoundError

from ..repositories import meals as meals_repo
from ..schemas.common import MealItem, MealItemRequest, MealItemUpdateRequest, MealRequest
from ..services.utils import ensure_valid_date

router = APIRouter(prefix="/meals", tags=["meals"])


@router.post("", response_model=dict)
async def create_meal(request: MealRequest, conn=Depends(get_db_connection), user_id: str = Depends(get_user_id)) -> dict:  # type: ignore[name-defined]
    ensure_valid_date(request.date.isoformat())
    meal_id = await meals_repo.create_meal(conn, user_id, request.date, request.meal_type.value, request.meal_time)
    return {"meal_id": meal_id}


@router.get("/{meal_id}")
async def get_meal(meal_id: str, conn=Depends(get_db_connection), user_id: str = Depends(get_user_id)) -> dict:  # type: ignore[name-defined]
    meal = await meals_repo.get_meal(conn, user_id, meal_id)
    if not meal:
        raise NotFoundError("Meal not found")

    items = await meals_repo.get_meal_items(conn, user_id, meal_id)
    return {"meal": dict(meal), "items": [MealItem(**dict(item)) for item in items]}


@router.delete("/{meal_id}")
async def delete_meal(meal_id: str, conn=Depends(get_db_connection), user_id: str = Depends(get_user_id)) -> dict:  # type: ignore[name-defined]
    deleted = await meals_repo.delete_meal(conn, user_id, meal_id)
    if not deleted:
        raise NotFoundError("Meal not found")
    return {"status": "ok"}


@router.post("/{meal_id}/items")
async def create_meal_item(
    meal_id: str,
    request: MealItemRequest,
    conn=Depends(get_db_connection),
    user_id: str = Depends(get_user_id),
) -> MealItem:  # type: ignore[name-defined]
    item_id = await meals_repo.create_meal_item(conn, user_id, meal_id, request.product_id, request.grams, request.added_via)
    item = await meals_repo.get_meal_item(conn, user_id, item_id)
    if not item:
        raise NotFoundError("Meal item not found after creation")
    return MealItem(**dict(item))


@router.patch("/{meal_id}/items/{item_id}")
async def update_meal_item(
    meal_id: str,
    item_id: str,
    request: MealItemUpdateRequest,
    conn=Depends(get_db_connection),
    user_id: str = Depends(get_user_id),
) -> MealItem:  # type: ignore[name-defined]
    updated = await meals_repo.update_meal_item(conn, user_id, meal_id, item_id, request.grams)
    if not updated:
        raise NotFoundError("Meal item not found")
    item = await meals_repo.get_meal_item(conn, user_id, item_id)
    if not item:
        raise NotFoundError("Meal item not found after update")
    return MealItem(**dict(item))


@router.delete("/{meal_id}/items/{item_id}")
async def delete_meal_item(
    meal_id: str,
    item_id: str,
    conn=Depends(get_db_connection),
    user_id: str = Depends(get_user_id),
) -> dict:  # type: ignore[name-defined]
    deleted = await meals_repo.delete_meal_item(conn, user_id, meal_id, item_id)
    if not deleted:
        raise NotFoundError("Meal item not found")
    return {"status": "ok"}

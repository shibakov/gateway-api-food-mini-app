from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile

from ..dependencies import get_db_connection, get_user_id
from ..repositories import products as products_repo
from ..schemas.common import PhotoRecognitionResponse, ProductNutritionUpdate, ProductRequest, ProductSearchResult

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/search", response_model=list[ProductSearchResult])
async def search_products(q: str, conn=Depends(get_db_connection)) -> list[ProductSearchResult]:  # type: ignore[name-defined]
    records = await products_repo.search_products(conn, q)
    return [
        ProductSearchResult(
            product_id=str(record["product_id"]),
            name=record["name"],
            brand=record["brand"],
            nutrition_per_100g={
                "calories": record["calories"],
                "protein": record["protein"],
                "fat": record["fat"],
                "carbs": record["carbs"],
            },
        )
        for record in records
    ]


@router.post("", response_model=dict)
async def create_product(
    request: ProductRequest,
    conn=Depends(get_db_connection),
    user_id: str = Depends(get_user_id),
) -> dict:  # type: ignore[name-defined]
    product_id = await products_repo.create_product(conn, request.name, request.brand, user_id)
    await products_repo.insert_nutrition_event(
        conn,
        product_id,
        request.nutrition_per_100g.calories,
        request.nutrition_per_100g.protein,
        request.nutrition_per_100g.fat,
        request.nutrition_per_100g.carbs,
        source="manual",
    )
    return {"product_id": product_id}


@router.patch("/{product_id}/nutrition")
async def update_product_nutrition(
    product_id: str,
    request: ProductNutritionUpdate,
    conn=Depends(get_db_connection),
    user_id: str = Depends(get_user_id),
) -> dict:  # type: ignore[name-defined]
    await products_repo.insert_nutrition_event(
        conn,
        product_id,
        request.nutrition_per_100g.calories,
        request.nutrition_per_100g.protein,
        request.nutrition_per_100g.fat,
        request.nutrition_per_100g.carbs,
        source="correction",
    )
    return {"status": "ok"}


@router.post("/recognize-photo", response_model=PhotoRecognitionResponse)
async def recognize_photo(files: list[UploadFile] = File(...)) -> PhotoRecognitionResponse:  # type: ignore[name-defined]
    # Stub implementation per clarification document
    _ = files  # ensure files are consumed
    return PhotoRecognitionResponse(status="not_implemented", results=[])

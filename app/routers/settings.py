from __future__ import annotations

from fastapi import APIRouter, Depends

from ..dependencies import get_db_connection, get_user_id
from ..errors import InternalError, NotFoundError

from ..repositories import settings as settings_repo
from ..schemas.common import Settings

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=Settings)
async def get_settings(conn=Depends(get_db_connection), user_id: str = Depends(get_user_id)) -> Settings:  # type: ignore[name-defined]
    record = await settings_repo.get_settings(conn, user_id)
    if not record:
        raise NotFoundError("Settings not found")
    return Settings(**dict(record))


@router.patch("", response_model=dict)
async def update_settings(
    request: Settings,
    conn=Depends(get_db_connection),
    user_id: str = Depends(get_user_id),
) -> dict:  # type: ignore[name-defined]
    # Pydantic validators already enforce step rules
    try:
        updated = await settings_repo.update_settings(
            conn,
            user_id,
            request.calorie_target,
            request.calorie_tolerance,
            request.macro_mode,
            request.protein_target,
            request.fat_target,
            request.carbs_target,
        )
        if not updated:
            raise NotFoundError("Settings not found")
        return {"status": "ok"}
    except NotFoundError:
        # Bubble up domain-specific not-found error for unified handling
        raise
    except Exception:
        # Ensure no unhandled exceptions leak from this handler
        raise InternalError()


@router.options("", include_in_schema=False)
async def options_settings() -> dict:
    # Explicit OPTIONS handler to ensure CORS preflight for /v1/settings always returns 200
    return {"status": "ok"}

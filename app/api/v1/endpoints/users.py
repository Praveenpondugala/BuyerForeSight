# app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime, timezone
from app.db.database import get_db
from app.services.user_service import UserService
from app.models.user import UserRole
from app.schemas.user import (
    UserCreate, UserUpdate, UserQueryParams,
    ApiResponse, PaginatedUsers, UserResponse,
)

router = APIRouter(prefix="/users", tags=["Users"])


def get_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)


def _now() -> datetime:
    return datetime.now(timezone.utc)


@router.get(
    "",
    response_model=ApiResponse[PaginatedUsers],
    summary="List users",
    description="Retrieve a paginated list of users with optional search, sort, and filters.",
)
async def list_users(
    search: Optional[str] = Query(None, description="Search name, email, or department"),
    sort: Optional[str] = Query("created_at", description="Sort field: name|email|department|created_at|updated_at"),
    order: Optional[str] = Query("asc", description="asc or desc"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    service: UserService = Depends(get_service),
):
    params = UserQueryParams(
        search=search, sort=sort, order=order,
        page=page, limit=limit, role=role, is_active=is_active,
    )
    result = await service.list_users(params)
    return ApiResponse(success=True, message="Users retrieved successfully", data=result, timestamp=_now())


@router.get(
    "/{user_id}",
    response_model=ApiResponse[UserResponse],
    summary="Get user by ID",
)
async def get_user(
    user_id: str,
    service: UserService = Depends(get_service),
):
    user = await service.get_user(user_id)
    return ApiResponse(success=True, message="User retrieved successfully", data=user, timestamp=_now())


@router.post(
    "",
    response_model=ApiResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
)
async def create_user(
    payload: UserCreate,
    service: UserService = Depends(get_service),
):
    user = await service.create_user(payload)
    return ApiResponse(success=True, message="User created successfully", data=user, timestamp=_now())


@router.put(
    "/{user_id}",
    response_model=ApiResponse[UserResponse],
    summary="Update a user",
)
async def update_user(
    user_id: str,
    payload: UserUpdate,
    service: UserService = Depends(get_service),
):
    user = await service.update_user(user_id, payload)
    return ApiResponse(success=True, message="User updated successfully", data=user, timestamp=_now())


@router.delete(
    "/{user_id}",
    response_model=ApiResponse[None],
    summary="Delete a user",
)
async def delete_user(
    user_id: str,
    service: UserService = Depends(get_service),
):
    await service.delete_user(user_id)
    return ApiResponse(success=True, message="User deleted successfully", timestamp=_now())

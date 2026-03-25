# app/services/user_service.py
import math
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.services.user_repository import UserRepository
from app.schemas.user import (
    UserCreate, UserUpdate, UserQueryParams,
    PaginatedUsers, PaginationMeta, UserResponse,
)
from app.core.logging import logger


class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def list_users(self, params: UserQueryParams) -> PaginatedUsers:
        users, total = await self.repo.get_all(params)
        total_pages = math.ceil(total / params.limit) if total > 0 else 1
        return PaginatedUsers(
            data=[UserResponse.model_validate(u) for u in users],
            pagination=PaginationMeta(
                total=total,
                page=params.page,
                limit=params.limit,
                total_pages=total_pages,
                has_next=params.page < total_pages,
                has_prev=params.page > 1,
            ),
        )

    async def get_user(self, user_id: str) -> UserResponse:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id '{user_id}' not found",
            )
        return UserResponse.model_validate(user)

    async def create_user(self, data: UserCreate) -> UserResponse:
        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A user with email '{data.email}' already exists",
            )
        user = await self.repo.create(data)
        logger.info(f"Created user id={user.id} email={user.email}")
        return UserResponse.model_validate(user)

    async def update_user(self, user_id: str, data: UserUpdate) -> UserResponse:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id '{user_id}' not found",
            )
        if data.email and data.email.lower() != user.email:
            conflict = await self.repo.get_by_email(data.email)
            if conflict:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Email '{data.email}' is already taken by another user",
                )
        updated = await self.repo.update(user, data)
        logger.info(f"Updated user id={updated.id}")
        return UserResponse.model_validate(updated)

    async def delete_user(self, user_id: str) -> None:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id '{user_id}' not found",
            )
        await self.repo.delete(user)
        logger.info(f"Deleted user id={user_id}")

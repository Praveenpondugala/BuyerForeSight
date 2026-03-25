# app/services/user_repository.py
import uuid
from datetime import datetime, timezone
from typing import Optional, Tuple, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, asc, desc
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, UserQueryParams


SORTABLE_COLUMNS = {
    "name": User.name,
    "email": User.email,
    "department": User.department,
    "created_at": User.created_at,
    "updated_at": User.updated_at,
}


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── List with filters, sort, pagination ───────────────────────────────────

    async def get_all(self, params: UserQueryParams) -> Tuple[List[User], int]:
        query = select(User)
        count_query = select(func.count()).select_from(User)

        # Search filter
        if params.search:
            term = f"%{params.search.strip()}%"
            search_filter = or_(
                User.name.ilike(term),
                User.email.ilike(term),
                User.department.ilike(term),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        # Role filter
        if params.role:
            query = query.where(User.role == params.role)
            count_query = count_query.where(User.role == params.role)

        # Active status filter
        if params.is_active is not None:
            query = query.where(User.is_active == params.is_active)
            count_query = count_query.where(User.is_active == params.is_active)

        # Total count (before pagination)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Sorting
        sort_col = SORTABLE_COLUMNS.get(params.sort or "created_at", User.created_at)
        order_fn = asc if (params.order or "asc").lower() == "asc" else desc
        query = query.order_by(order_fn(sort_col))

        # Pagination
        offset = (params.page - 1) * params.limit
        query = query.offset(offset).limit(params.limit)

        result = await self.db.execute(query)
        users = list(result.scalars().all())
        return users, total

    # ── Get single ────────────────────────────────────────────────────────────

    async def get_by_id(self, user_id: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email.lower()))
        return result.scalar_one_or_none()

    # ── Create ────────────────────────────────────────────────────────────────

    async def create(self, data: UserCreate) -> User:
        user = User(
            id=str(uuid.uuid4()),
            name=data.name.strip(),
            email=data.email.lower(),
            role=data.role,
            department=data.department.strip(),
            phone=data.phone,
            avatar=data.avatar,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    # ── Update ────────────────────────────────────────────────────────────────

    async def update(self, user: User, data: UserUpdate) -> User:
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return user

        if "email" in update_data:
            update_data["email"] = update_data["email"].lower()
        if "name" in update_data and update_data["name"]:
            update_data["name"] = update_data["name"].strip()

        update_data["updated_at"] = datetime.now(timezone.utc)

        for field, value in update_data.items():
            setattr(user, field, value)

        await self.db.flush()
        await self.db.refresh(user)
        return user

    # ── Delete ────────────────────────────────────────────────────────────────

    async def delete(self, user: User) -> None:
        await self.db.delete(user)
        await self.db.flush()

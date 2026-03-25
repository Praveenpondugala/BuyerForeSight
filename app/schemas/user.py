# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional, Generic, TypeVar, List
from datetime import datetime, timezone
from app.models.user import UserRole
import re

T = TypeVar("T")


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


# ── Request Schemas ──────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, examples=["Alice Johnson"])
    email: EmailStr = Field(..., examples=["alice@company.com"])
    role: UserRole = Field(default=UserRole.EMPLOYEE)
    department: str = Field(..., min_length=2, max_length=100, examples=["Engineering"])
    phone: Optional[str] = Field(None, examples=["+91-9876543210"])
    avatar: Optional[str] = Field(None, examples=["https://example.com/avatar.png"])

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name must not be blank")
        return v.strip()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        cleaned = re.sub(r"[\s\-\(\)]", "", v)
        if not re.match(r"^\+?[\d]{7,15}$", cleaned):
            raise ValueError("Invalid phone number format")
        return v


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    department: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = None
    avatar: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("name")
    @classmethod
    def name_strip(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if v else v


# ── Query Params ─────────────────────────────────────────────────────────────

class UserQueryParams(BaseModel):
    search: Optional[str] = Field(None, description="Search by name, email, or department")
    sort: Optional[str] = Field("created_at", description="Sort field: name|email|department|created_at")
    order: Optional[str] = Field("asc", description="Sort order: asc|desc")
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(10, ge=1, le=100, description="Items per page")
    role: Optional[UserRole] = Field(None, description="Filter by role")
    is_active: Optional[bool] = Field(None, description="Filter by active status")

    @field_validator("sort")
    @classmethod
    def validate_sort(cls, v: Optional[str]) -> Optional[str]:
        allowed = {"name", "email", "department", "created_at", "updated_at"}
        if v and v not in allowed:
            raise ValueError(f"sort must be one of: {', '.join(sorted(allowed))}")
        return v

    @field_validator("order")
    @classmethod
    def validate_order(cls, v: Optional[str]) -> Optional[str]:
        if v and v.lower() not in {"asc", "desc"}:
            raise ValueError("order must be 'asc' or 'desc'")
        return v.lower() if v else v


# ── Response Schemas ──────────────────────────────────────────────────────────

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: str
    role: UserRole
    department: str
    phone: Optional[str]
    avatar: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PaginationMeta(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedUsers(BaseModel):
    data: List[UserResponse]
    pagination: PaginationMeta


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
    timestamp: datetime = Field(default_factory=_now_utc)

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    errors: Optional[List[ErrorDetail]] = None
    timestamp: datetime = Field(default_factory=_now_utc)

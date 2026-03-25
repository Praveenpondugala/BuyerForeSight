# app/utils/seeder.py
import asyncio
import uuid
from datetime import datetime, timezone, timedelta
import random
from app.db.database import AsyncSessionLocal, init_db
from app.models.user import User, UserRole


SEED_USERS = [
    {"name": "Arjun Sharma",    "email": "arjun.sharma@buyerforesight.com",    "role": UserRole.ADMIN,    "department": "Engineering",  "phone": "+91-9876543210"},
    {"name": "Priya Nair",      "email": "priya.nair@buyerforesight.com",      "role": UserRole.MANAGER,  "department": "Product",      "phone": "+91-9812345678"},
    {"name": "Rahul Mehta",     "email": "rahul.mehta@buyerforesight.com",     "role": UserRole.EMPLOYEE, "department": "Engineering",  "phone": "+91-9823456789"},
    {"name": "Sneha Patel",     "email": "sneha.patel@buyerforesight.com",     "role": UserRole.EMPLOYEE, "department": "Design",       "phone": "+91-9834567890"},
    {"name": "Vikram Singh",    "email": "vikram.singh@buyerforesight.com",    "role": UserRole.MANAGER,  "department": "Sales",        "phone": "+91-9845678901"},
    {"name": "Ananya Reddy",    "email": "ananya.reddy@buyerforesight.com",    "role": UserRole.EMPLOYEE, "department": "Marketing",    "phone": "+91-9856789012"},
    {"name": "Karan Gupta",     "email": "karan.gupta@buyerforesight.com",     "role": UserRole.EMPLOYEE, "department": "Engineering",  "phone": "+91-9867890123"},
    {"name": "Divya Krishnan",  "email": "divya.krishnan@buyerforesight.com",  "role": UserRole.VIEWER,   "department": "Finance",      "phone": "+91-9878901234"},
    {"name": "Rohan Joshi",     "email": "rohan.joshi@buyerforesight.com",     "role": UserRole.EMPLOYEE, "department": "Engineering",  "phone": "+91-9889012345"},
    {"name": "Meera Iyer",      "email": "meera.iyer@buyerforesight.com",      "role": UserRole.MANAGER,  "department": "HR",           "phone": "+91-9890123456"},
    {"name": "Aditya Kumar",    "email": "aditya.kumar@buyerforesight.com",    "role": UserRole.EMPLOYEE, "department": "Data Science", "phone": "+91-9901234567"},
    {"name": "Pooja Verma",     "email": "pooja.verma@buyerforesight.com",     "role": UserRole.EMPLOYEE, "department": "QA",           "phone": "+91-9812345679"},
    {"name": "Sanjay Bhatt",    "email": "sanjay.bhatt@buyerforesight.com",    "role": UserRole.ADMIN,    "department": "Engineering",  "phone": "+91-9823456780"},
    {"name": "Lakshmi Chandran","email": "lakshmi.chandran@buyerforesight.com","role": UserRole.VIEWER,   "department": "Legal",        "phone": "+91-9834567891"},
    {"name": "Nikhil Agarwal",  "email": "nikhil.agarwal@buyerforesight.com",  "role": UserRole.EMPLOYEE, "department": "DevOps",       "phone": "+91-9845678902"},
]


async def seed() -> None:
    await init_db()
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select, func
        count_result = await session.execute(select(func.count()).select_from(User))
        if count_result.scalar_one() > 0:
            return  # already seeded

        base_time = datetime.now(timezone.utc) - timedelta(days=90)
        for i, u in enumerate(SEED_USERS):
            created_at = base_time + timedelta(days=i * 5, hours=random.randint(0, 23))
            session.add(User(
                id=str(uuid.uuid4()),
                name=u["name"],
                email=u["email"],
                role=u["role"],
                department=u["department"],
                phone=u.get("phone"),
                is_active=True,
                created_at=created_at,
                updated_at=created_at,
            ))

        await session.commit()
        print(f"✅ Seeded {len(SEED_USERS)} users.")


if __name__ == "__main__":
    asyncio.run(seed())

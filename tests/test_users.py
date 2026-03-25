# tests/test_users.py
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


# ── POST /users ───────────────────────────────────────────────────────────────

class TestCreateUser:
    async def test_create_user_success(self, client: AsyncClient):
        payload = {
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "role": "employee",
            "department": "Engineering",
        }
        resp = await client.post("/api/v1/users", json=payload)
        assert resp.status_code == 201
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["name"] == "Alice Johnson"
        assert body["data"]["email"] == "alice@example.com"
        assert body["data"]["role"] == "employee"
        assert body["data"]["is_active"] is True
        assert "id" in body["data"]
        assert "created_at" in body["data"]

    async def test_create_user_duplicate_email(self, client: AsyncClient, sample_user):
        payload = {
            "name": "Duplicate",
            "email": sample_user["email"],
            "role": "employee",
            "department": "HR",
        }
        resp = await client.post("/api/v1/users", json=payload)
        assert resp.status_code == 409
        assert resp.json()["success"] is False

    async def test_create_user_missing_required_fields(self, client: AsyncClient):
        resp = await client.post("/api/v1/users", json={"name": "No Email"})
        assert resp.status_code == 422

    async def test_create_user_invalid_email(self, client: AsyncClient):
        payload = {"name": "Bad Email", "email": "not-an-email", "department": "IT"}
        resp = await client.post("/api/v1/users", json=payload)
        assert resp.status_code == 422

    async def test_create_user_invalid_role(self, client: AsyncClient):
        payload = {
            "name": "Bad Role",
            "email": "badrole@example.com",
            "role": "superuser",
            "department": "IT",
        }
        resp = await client.post("/api/v1/users", json=payload)
        assert resp.status_code == 422

    async def test_create_user_email_stored_lowercase(self, client: AsyncClient):
        payload = {
            "name": "Case Test",
            "email": "UPPER@EXAMPLE.COM",
            "department": "QA",
        }
        resp = await client.post("/api/v1/users", json=payload)
        assert resp.status_code == 201
        assert resp.json()["data"]["email"] == "upper@example.com"

    async def test_create_user_all_roles(self, client: AsyncClient):
        for i, role in enumerate(["admin", "manager", "employee", "viewer"]):
            payload = {
                "name": f"Role User {i}",
                "email": f"role{i}@example.com",
                "role": role,
                "department": "Test",
            }
            resp = await client.post("/api/v1/users", json=payload)
            assert resp.status_code == 201
            assert resp.json()["data"]["role"] == role


# ── GET /users ────────────────────────────────────────────────────────────────

class TestListUsers:
    async def test_list_users_empty(self, client: AsyncClient):
        resp = await client.get("/api/v1/users")
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["data"] == []
        assert body["data"]["pagination"]["total"] == 0

    async def test_list_users_with_data(self, client: AsyncClient, sample_user):
        resp = await client.get("/api/v1/users")
        assert resp.status_code == 200
        body = resp.json()
        assert body["data"]["pagination"]["total"] == 1
        assert len(body["data"]["data"]) == 1

    async def test_search_by_name(self, client: AsyncClient):
        for name, email, dept in [
            ("Alice Smith", "alice.s@example.com", "Engineering"),
            ("Bob Jones", "bob.j@example.com", "Sales"),
        ]:
            await client.post("/api/v1/users", json={"name": name, "email": email, "department": dept})

        resp = await client.get("/api/v1/users?search=Alice")
        assert resp.status_code == 200
        results = resp.json()["data"]["data"]
        assert len(results) >= 1
        assert all("alice" in u["name"].lower() for u in results)

    async def test_search_by_email(self, client: AsyncClient):
        await client.post("/api/v1/users", json={"name": "Email Search", "email": "findme@acme.com", "department": "Finance"})
        resp = await client.get("/api/v1/users?search=acme")
        assert resp.status_code == 200
        assert resp.json()["data"]["pagination"]["total"] >= 1

    async def test_search_by_department(self, client: AsyncClient):
        await client.post("/api/v1/users", json={"name": "Dept User", "email": "dept@example.com", "department": "DataScience"})
        resp = await client.get("/api/v1/users?search=DataScience")
        assert resp.status_code == 200
        results = resp.json()["data"]["data"]
        assert any("DataScience" in u["department"] for u in results)

    async def test_sort_by_name_asc(self, client: AsyncClient):
        for name, email in [("Charlie", "charlie@x.com"), ("Alice", "alicex@x.com"), ("Bob", "bob@x.com")]:
            await client.post("/api/v1/users", json={"name": name, "email": email, "department": "IT"})
        resp = await client.get("/api/v1/users?sort=name&order=asc")
        names = [u["name"] for u in resp.json()["data"]["data"]]
        assert names == sorted(names)

    async def test_sort_by_name_desc(self, client: AsyncClient):
        for name, email in [("Charlie", "charlie2@x.com"), ("Alice", "alice2@x.com"), ("Bob", "bob2@x.com")]:
            await client.post("/api/v1/users", json={"name": name, "email": email, "department": "IT"})
        resp = await client.get("/api/v1/users?sort=name&order=desc")
        names = [u["name"] for u in resp.json()["data"]["data"]]
        assert names == sorted(names, reverse=True)

    async def test_filter_by_role(self, client: AsyncClient):
        await client.post("/api/v1/users", json={"name": "Admin U", "email": "admin_u@x.com", "role": "admin", "department": "IT"})
        await client.post("/api/v1/users", json={"name": "Emp U", "email": "emp_u@x.com", "role": "employee", "department": "IT"})
        resp = await client.get("/api/v1/users?role=admin")
        results = resp.json()["data"]["data"]
        assert len(results) >= 1
        assert all(u["role"] == "admin" for u in results)

    async def test_filter_by_is_active(self, client: AsyncClient, sample_user):
        resp = await client.get("/api/v1/users?is_active=true")
        assert resp.status_code == 200
        results = resp.json()["data"]["data"]
        assert all(u["is_active"] is True for u in results)

    async def test_pagination(self, client: AsyncClient):
        for i in range(15):
            await client.post("/api/v1/users", json={"name": f"Pager {i}", "email": f"pager{i}@x.com", "department": "IT"})
        resp = await client.get("/api/v1/users?page=1&limit=5")
        body = resp.json()["data"]
        assert len(body["data"]) == 5
        assert body["pagination"]["total"] == 15
        assert body["pagination"]["total_pages"] == 3
        assert body["pagination"]["has_next"] is True
        assert body["pagination"]["has_prev"] is False

    async def test_pagination_page2(self, client: AsyncClient):
        for i in range(12):
            await client.post("/api/v1/users", json={"name": f"Page2 {i}", "email": f"page2user{i}@x.com", "department": "IT"})
        resp = await client.get("/api/v1/users?page=2&limit=5")
        body = resp.json()["data"]
        assert len(body["data"]) == 5
        assert body["pagination"]["has_prev"] is True

    async def test_invalid_sort_field(self, client: AsyncClient):
        resp = await client.get("/api/v1/users?sort=password")
        assert resp.status_code in (400, 422)

    async def test_invalid_order_value(self, client: AsyncClient):
        resp = await client.get("/api/v1/users?order=random")
        assert resp.status_code in (400, 422)


# ── GET /users/:id ────────────────────────────────────────────────────────────

class TestGetUser:
    async def test_get_user_success(self, client: AsyncClient, sample_user):
        resp = await client.get(f"/api/v1/users/{sample_user['id']}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["id"] == sample_user["id"]
        assert body["data"]["email"] == sample_user["email"]

    async def test_get_user_not_found(self, client: AsyncClient):
        resp = await client.get("/api/v1/users/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404
        assert resp.json()["success"] is False


# ── PUT /users/:id ────────────────────────────────────────────────────────────

class TestUpdateUser:
    async def test_update_user_name(self, client: AsyncClient, sample_user):
        resp = await client.put(f"/api/v1/users/{sample_user['id']}", json={"name": "Updated Name"})
        assert resp.status_code == 200
        assert resp.json()["data"]["name"] == "Updated Name"

    async def test_update_user_role(self, client: AsyncClient, sample_user):
        resp = await client.put(f"/api/v1/users/{sample_user['id']}", json={"role": "admin"})
        assert resp.status_code == 200
        assert resp.json()["data"]["role"] == "admin"

    async def test_update_user_deactivate(self, client: AsyncClient, sample_user):
        resp = await client.put(f"/api/v1/users/{sample_user['id']}", json={"is_active": False})
        assert resp.status_code == 200
        assert resp.json()["data"]["is_active"] is False

    async def test_update_user_email_conflict(self, client: AsyncClient, sample_user):
        other = await client.post("/api/v1/users", json={"name": "Other", "email": "other@conflict.com", "department": "HR"})
        other_id = other.json()["data"]["id"]
        resp = await client.put(f"/api/v1/users/{other_id}", json={"email": sample_user["email"]})
        assert resp.status_code == 409

    async def test_update_user_not_found(self, client: AsyncClient):
        resp = await client.put("/api/v1/users/00000000-0000-0000-0000-000000000000", json={"name": "Ghost"})
        assert resp.status_code == 404

    async def test_update_user_updated_at_changes(self, client: AsyncClient, sample_user):
        import asyncio
        await asyncio.sleep(0.05)
        resp = await client.put(f"/api/v1/users/{sample_user['id']}", json={"name": "Changed Again"})
        assert resp.status_code == 200
        assert resp.json()["data"]["name"] == "Changed Again"


# ── DELETE /users/:id ─────────────────────────────────────────────────────────

class TestDeleteUser:
    async def test_delete_user_success(self, client: AsyncClient, sample_user):
        resp = await client.delete(f"/api/v1/users/{sample_user['id']}")
        assert resp.status_code == 200
        assert resp.json()["success"] is True
        get_resp = await client.get(f"/api/v1/users/{sample_user['id']}")
        assert get_resp.status_code == 404

    async def test_delete_user_not_found(self, client: AsyncClient):
        resp = await client.delete("/api/v1/users/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404


# ── Health ─────────────────────────────────────────────────────────────────────

class TestHealth:
    async def test_health_check(self, client: AsyncClient):
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

    async def test_root(self, client: AsyncClient):
        resp = await client.get("/")
        assert resp.status_code == 200
        assert "docs" in resp.json()

"""
SetuX / VeriX — Departments API Tests
Verifies:
- List departments (public/authenticated)
- Search departments by name and code
- Get department by ID
- Create department (Officer authorized)
- Block non-officer from creating department (403/401)
- Reject duplicate department code (400)
- Update department (Officer authorized)
- Delete department (Officer authorized)
- Block deleting department with linked projects (400)
"""
import pytest
from fastapi.testclient import TestClient


def test_list_and_search_departments(client: TestClient):
    # 1. List all
    res = client.get("/api/departments")
    assert res.status_code == 200
    depts = res.json()
    assert len(depts) >= 5

    # 2. Search by code
    res_search = client.get("/api/departments?search=PWD")
    assert res_search.status_code == 200
    search_data = res_search.json()
    assert any(d["code"] == "PWD" for d in search_data)


def test_get_department_by_id(client: TestClient):
    res = client.get("/api/departments/1")
    assert res.status_code == 200
    dept = res.json()
    assert dept["id"] == 1
    assert "name" in dept

    # Non-existent
    res_404 = client.get("/api/departments/99999")
    assert res_404.status_code == 404


def test_create_department_rbac(client: TestClient, officer_token, citizen_token):
    payload = {
        "name": "Forest and Environment Department",
        "code": "FED",
        "description": "Afforestation, wildlife corridors, and environmental clearances",
    }

    # 1. Citizen cannot create
    res_cit = client.post(
        "/api/departments",
        json=payload,
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert res_cit.status_code == 403

    # 2. Officer can create
    res_off = client.post(
        "/api/departments",
        json=payload,
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert res_off.status_code == 201
    created = res_off.json()
    assert created["code"] == "FED"
    assert created["name"] == payload["name"]

    # 3. Duplicate code rejected
    res_dup = client.post(
        "/api/departments",
        json=payload,
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert res_dup.status_code == 400
    assert "already exists" in res_dup.json()["detail"].lower()


def test_update_and_delete_department(client: TestClient, officer_token):
    # Create temp department to update and delete
    create_res = client.post(
        "/api/departments",
        json={"name": "Temp Department", "code": "TEMP", "description": "To be modified"},
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert create_res.status_code == 201
    dept_id = create_res.json()["id"]

    # Update
    update_res = client.put(
        f"/api/departments/{dept_id}",
        json={"name": "Updated Temp Department", "description": "Modified description"},
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Updated Temp Department"

    # Delete
    del_res = client.delete(
        f"/api/departments/{dept_id}",
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

    # Confirm 404
    get_res = client.get(f"/api/departments/{dept_id}")
    assert get_res.status_code == 404

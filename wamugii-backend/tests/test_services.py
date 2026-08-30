def test_create_service_as_admin(client, admin_headers):
    resp = client.post(
        "/api/v1/services",
        json={"name": "Web Design & Development"},
        headers=admin_headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Web Design & Development"
    assert body["slug"] == "web-design-development"
    assert body["is_active"] is True


def test_create_service_as_client_forbidden(client, client_headers):
    resp = client.post("/api/v1/services", json={"name": "X"}, headers=client_headers)
    assert resp.status_code == 403


def test_create_service_unauthenticated(client):
    resp = client.post("/api/v1/services", json={"name": "X"})
    assert resp.status_code == 401


def test_list_services_public_only_active(client, admin_headers):
    client.post("/api/v1/services", json={"name": "Active One"}, headers=admin_headers)
    inactive = client.post(
        "/api/v1/services", json={"name": "Inactive One"}, headers=admin_headers
    ).json()
    client.delete(f"/api/v1/services/{inactive['id']}", headers=admin_headers)

    resp = client.get("/api/v1/services")
    assert resp.status_code == 200
    names = [s["name"] for s in resp.json()]
    assert "Active One" in names
    assert "Inactive One" not in names


def test_get_single_active_service_public(client, admin_headers):
    created = client.post(
        "/api/v1/services", json={"name": "Public Service"}, headers=admin_headers
    ).json()
    resp = client.get(f"/api/v1/services/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Public Service"


def test_update_service_as_admin(client, admin_headers):
    created = client.post(
        "/api/v1/services", json={"name": "Old Name"}, headers=admin_headers
    ).json()
    resp = client.patch(
        f"/api/v1/services/{created['id']}",
        json={"name": "New Name"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"


def test_soft_delete_service_as_admin(client, admin_headers):
    created = client.post(
        "/api/v1/services", json={"name": "To Delete"}, headers=admin_headers
    ).json()
    resp = client.delete(f"/api/v1/services/{created['id']}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False

    listed = client.get("/api/v1/services").json()
    assert all(s["id"] != created["id"] for s in listed)


def test_filter_by_category_and_search_by_name(client, admin_headers):
    client.post(
        "/api/v1/services",
        json={"name": "Web Hosting", "category": "hosting"},
        headers=admin_headers,
    )
    client.post(
        "/api/v1/services",
        json={"name": "Domain Registration", "category": "hosting"},
        headers=admin_headers,
    )
    client.post(
        "/api/v1/services",
        json={"name": "Software Development", "category": "software"},
        headers=admin_headers,
    )

    by_category = client.get("/api/v1/services", params={"category": "hosting"}).json()
    assert {s["name"] for s in by_category} == {"Web Hosting", "Domain Registration"}

    by_search = client.get("/api/v1/services", params={"search": "web"}).json()
    assert {s["name"] for s in by_search} == {"Web Hosting"}

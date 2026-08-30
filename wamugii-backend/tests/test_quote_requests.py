QUOTE_PAYLOAD = {
    "full_name": "Jane Doe",
    "email": "jane@example.com",
    "phone": "+250780000000",
    "project_title": "New company website",
    "project_description": "We need a marketing website with a blog.",
}


def test_public_can_create_quote_request(client):
    resp = client.post("/api/v1/quote-requests", json=QUOTE_PAYLOAD)
    assert resp.status_code == 201
    body = resp.json()
    assert body["full_name"] == "Jane Doe"
    assert body["status"] == "NEW"


def test_new_quote_defaults_to_status_new(client):
    resp = client.post("/api/v1/quote-requests", json=QUOTE_PAYLOAD)
    assert resp.json()["status"] == "NEW"


def test_nonexistent_service_id_rejected(client):
    payload = {**QUOTE_PAYLOAD, "service_id": 999}
    resp = client.post("/api/v1/quote-requests", json=payload)
    assert resp.status_code == 422


def test_inactive_service_id_rejected(client, admin_headers):
    created = client.post(
        "/api/v1/services", json={"name": "Temp Service"}, headers=admin_headers
    ).json()
    client.delete(f"/api/v1/services/{created['id']}", headers=admin_headers)

    payload = {**QUOTE_PAYLOAD, "service_id": created["id"]}
    resp = client.post("/api/v1/quote-requests", json=payload)
    assert resp.status_code == 422


def test_public_response_has_no_admin_notes(client):
    resp = client.post("/api/v1/quote-requests", json=QUOTE_PAYLOAD)
    assert "admin_notes" not in resp.json()


def test_public_cannot_set_status_or_admin_notes(client):
    payload = {**QUOTE_PAYLOAD, "status": "ACCEPTED", "admin_notes": "sneaky"}
    resp = client.post("/api/v1/quote-requests", json=payload)
    assert resp.status_code == 201
    assert resp.json()["status"] == "NEW"
    assert "admin_notes" not in resp.json()


def test_unauthenticated_cannot_list(client):
    resp = client.get("/api/v1/quote-requests")
    assert resp.status_code == 401


def test_client_cannot_list(client, client_headers):
    resp = client.get("/api/v1/quote-requests", headers=client_headers)
    assert resp.status_code == 403


def test_admin_and_staff_can_list(client, admin_headers, staff_headers):
    client.post("/api/v1/quote-requests", json=QUOTE_PAYLOAD)

    resp_admin = client.get("/api/v1/quote-requests", headers=admin_headers)
    assert resp_admin.status_code == 200
    assert len(resp_admin.json()) == 1

    resp_staff = client.get("/api/v1/quote-requests", headers=staff_headers)
    assert resp_staff.status_code == 200
    assert len(resp_staff.json()) == 1


def test_staff_can_update_status_and_notes(client, staff_headers):
    created = client.post("/api/v1/quote-requests", json=QUOTE_PAYLOAD).json()
    resp = client.patch(
        f"/api/v1/quote-requests/{created['id']}",
        json={"status": "REVIEWING", "admin_notes": "Looks good, following up"},
        headers=staff_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "REVIEWING"
    assert body["admin_notes"] == "Looks good, following up"


def test_admin_soft_delete_hides_from_default_list(client, admin_headers):
    created = client.post("/api/v1/quote-requests", json=QUOTE_PAYLOAD).json()
    resp = client.delete(f"/api/v1/quote-requests/{created['id']}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False

    listed = client.get("/api/v1/quote-requests", headers=admin_headers).json()
    assert all(q["id"] != created["id"] for q in listed)

    listed_all = client.get(
        "/api/v1/quote-requests", params={"include_inactive": True}, headers=admin_headers
    ).json()
    assert any(q["id"] == created["id"] for q in listed_all)


def test_dashboard_quotes_pending_counts_new_and_reviewing_only(client, admin_headers):
    q1 = client.post("/api/v1/quote-requests", json=QUOTE_PAYLOAD).json()
    q2 = client.post("/api/v1/quote-requests", json=QUOTE_PAYLOAD).json()
    q3 = client.post("/api/v1/quote-requests", json=QUOTE_PAYLOAD).json()
    q4 = client.post("/api/v1/quote-requests", json=QUOTE_PAYLOAD).json()

    client.patch(
        f"/api/v1/quote-requests/{q2['id']}", json={"status": "REVIEWING"}, headers=admin_headers
    )
    client.patch(
        f"/api/v1/quote-requests/{q3['id']}", json={"status": "REJECTED"}, headers=admin_headers
    )
    client.delete(f"/api/v1/quote-requests/{q4['id']}", headers=admin_headers)
    # q4 was still NEW but is soft-deleted, so it must not count

    resp = client.get("/api/v1/admin/dashboard", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["quotes"]["pending"] == 2  # q1 (NEW) + q2 (REVIEWING)

from app.core.security import create_access_token
from app.crud import user as user_crud
from app.models.user import Role
from app.schemas.user import UserCreate
from tests.conftest import TestingSessionLocal


def _create_client(email: str, full_name: str = "Invoice Client"):
    db = TestingSessionLocal()
    try:
        return user_crud.create(
            db,
            UserCreate(full_name=full_name, email=email, password="password123"),
            role=Role.CLIENT,
        )
    finally:
        db.close()


def _client_auth_headers(user) -> dict:
    return {"Authorization": f"Bearer {create_access_token(user.id)}"}


def _create_project(client, admin_headers, client_id: int, title: str = "Linked Project") -> dict:
    return client.post(
        "/api/v1/projects",
        json={"client_id": client_id, "title": title, "description": "d"},
        headers=admin_headers,
    ).json()


def _create_invoice(client, headers, **overrides) -> dict:
    payload = {"client_id": overrides.pop("client_id"), "subtotal": "1000.00"}
    payload.update(overrides)
    return client.post("/api/v1/invoices", json=payload, headers=headers)


# --- creation & permissions ------------------------------------------------


def test_admin_can_create_invoice(client, admin_headers):
    c = _create_client("inv_admin@example.com")
    resp = _create_invoice(client, admin_headers, client_id=c.id)
    assert resp.status_code == 201
    body = resp.json()
    assert body["client_id"] == c.id
    assert body["status"] == "DRAFT"
    assert body["invoice_number"].startswith("WAM-")
    # Money surfaces as decimal strings, like projects.budget.
    assert body["total"] == "1000.00"
    assert body["amount_paid"] == "0.00"
    assert body["balance_due"] == "1000.00"


def test_staff_can_create_invoice(client, staff_headers):
    c = _create_client("inv_staff@example.com")
    resp = _create_invoice(client, staff_headers, client_id=c.id)
    assert resp.status_code == 201


def test_client_cannot_create_invoice(client, client_headers):
    c = _create_client("inv_target@example.com")
    resp = _create_invoice(client, client_headers, client_id=c.id)
    assert resp.status_code == 403


def test_unauthenticated_cannot_create_invoice(client):
    c = _create_client("inv_anon@example.com")
    resp = client.post("/api/v1/invoices", json={"client_id": c.id, "subtotal": "500.00"})
    assert resp.status_code == 401


def test_invoice_numbers_are_sequential_and_unique(client, admin_headers):
    c = _create_client("inv_seq@example.com")
    first = _create_invoice(client, admin_headers, client_id=c.id).json()
    second = _create_invoice(client, admin_headers, client_id=c.id).json()
    assert first["invoice_number"] != second["invoice_number"]
    assert int(second["invoice_number"].rsplit("-", 1)[1]) == (
        int(first["invoice_number"].rsplit("-", 1)[1]) + 1
    )


# --- standalone invoices (no project) --------------------------------------


def test_standalone_invoice_without_project_works(client, admin_headers):
    """An electronics sale or one-off consult has no project — that is valid."""
    c = _create_client("inv_standalone@example.com")
    resp = _create_invoice(client, admin_headers, client_id=c.id, subtotal="250.00")
    assert resp.status_code == 201
    body = resp.json()
    assert body["project_id"] is None
    assert body["total"] == "250.00"

    # ...and it is fully usable: readable, listable, and payable.
    invoice_id = body["id"]
    assert client.get(f"/api/v1/invoices/{invoice_id}", headers=admin_headers).status_code == 200
    listed = client.get("/api/v1/invoices", headers=admin_headers).json()
    assert invoice_id in [i["id"] for i in listed]

    paid = client.post(
        f"/api/v1/invoices/{invoice_id}/payments",
        json={"amount": "250.00", "method": "CASH"},
        headers=admin_headers,
    )
    assert paid.status_code == 201
    after = client.get(f"/api/v1/invoices/{invoice_id}", headers=admin_headers).json()
    assert after["status"] == "PAID"


def test_invoice_with_matching_project_is_accepted(client, admin_headers):
    c = _create_client("inv_match@example.com")
    project = _create_project(client, admin_headers, c.id)
    resp = _create_invoice(client, admin_headers, client_id=c.id, project_id=project["id"])
    assert resp.status_code == 201
    assert resp.json()["project_id"] == project["id"]


def test_project_client_mismatch_is_rejected(client, admin_headers):
    owner = _create_client("inv_owner@example.com")
    other = _create_client("inv_other@example.com")
    project = _create_project(client, admin_headers, owner.id)

    resp = _create_invoice(client, admin_headers, client_id=other.id, project_id=project["id"])
    assert resp.status_code == 422
    assert "different client" in resp.json()["detail"]


def test_invoice_requires_a_real_client(client, admin_headers):
    resp = _create_invoice(client, admin_headers, client_id=999999)
    assert resp.status_code == 422


# --- money & status derivation ---------------------------------------------


def test_totals_computed_from_line_items(client, admin_headers):
    c = _create_client("inv_items@example.com")
    resp = _create_invoice(
        client,
        admin_headers,
        client_id=c.id,
        subtotal="0.00",  # ignored — items win
        tax="100.00",
        discount="50.00",
        items=[
            {"description": "Laptop", "quantity": "2", "unit_price": "400.00"},
            {"description": "Setup", "quantity": "1", "unit_price": "200.00"},
        ],
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["subtotal"] == "1000.00"  # 2*400 + 1*200
    assert body["total"] == "1050.00"  # 1000 - 50 + 100
    assert [i["line_total"] for i in body["items"]] == ["800.00", "200.00"]


def test_client_cannot_dictate_total_or_status(client, admin_headers):
    """`total` is server-computed and money-derived statuses are rejected."""
    c = _create_client("inv_forge@example.com")
    resp = _create_invoice(
        client, admin_headers, client_id=c.id, subtotal="1000.00", total="1.00"
    )
    assert resp.status_code == 201
    assert resp.json()["total"] == "1000.00"  # the forged total is ignored

    forged = _create_invoice(
        client, admin_headers, client_id=c.id, subtotal="1000.00", status="PAID"
    )
    assert forged.status_code == 422


def test_balance_and_status_across_unpaid_partial_and_full(client, admin_headers):
    c = _create_client("inv_lifecycle@example.com")
    invoice = _create_invoice(
        client, admin_headers, client_id=c.id, subtotal="1000.00", status="SENT"
    ).json()
    invoice_id = invoice["id"]

    # Unpaid
    assert invoice["status"] == "SENT"
    assert invoice["balance_due"] == "1000.00"

    # Partial
    client.post(
        f"/api/v1/invoices/{invoice_id}/payments",
        json={"amount": "400.00", "method": "MOBILE_MONEY"},
        headers=admin_headers,
    )
    partial = client.get(f"/api/v1/invoices/{invoice_id}", headers=admin_headers).json()
    assert partial["status"] == "PARTIALLY_PAID"
    assert partial["amount_paid"] == "400.00"
    assert partial["balance_due"] == "600.00"

    # Full
    client.post(
        f"/api/v1/invoices/{invoice_id}/payments",
        json={"amount": "600.00", "method": "BANK_TRANSFER"},
        headers=admin_headers,
    )
    full = client.get(f"/api/v1/invoices/{invoice_id}", headers=admin_headers).json()
    assert full["status"] == "PAID"
    assert full["amount_paid"] == "1000.00"
    assert full["balance_due"] == "0.00"
    assert len(full["payments"]) == 2


def test_unpaid_sent_invoice_past_due_reads_as_overdue(client, admin_headers):
    c = _create_client("inv_overdue@example.com")
    invoice = _create_invoice(
        client,
        admin_headers,
        client_id=c.id,
        subtotal="300.00",
        status="SENT",
        due_date="2020-01-01T00:00:00Z",
    ).json()
    assert invoice["status"] == "OVERDUE"

    # Paying it still settles correctly from the OVERDUE state.
    client.post(
        f"/api/v1/invoices/{invoice['id']}/payments",
        json={"amount": "300.00", "method": "BANK_TRANSFER"},
        headers=admin_headers,
    )
    settled = client.get(f"/api/v1/invoices/{invoice['id']}", headers=admin_headers).json()
    assert settled["status"] == "PAID"


def test_draft_invoice_past_due_stays_draft(client, admin_headers):
    """An unsent draft is not chaseable, so it must not read as OVERDUE."""
    c = _create_client("inv_draftdue@example.com")
    invoice = _create_invoice(
        client, admin_headers, client_id=c.id, due_date="2020-01-01T00:00:00Z"
    ).json()
    assert invoice["status"] == "DRAFT"


def test_payment_cannot_exceed_balance(client, admin_headers):
    c = _create_client("inv_overpay@example.com")
    invoice = _create_invoice(client, admin_headers, client_id=c.id, subtotal="100.00").json()
    resp = client.post(
        f"/api/v1/invoices/{invoice['id']}/payments",
        json={"amount": "150.00", "method": "CASH"},
        headers=admin_headers,
    )
    assert resp.status_code == 422


def test_client_cannot_record_payment(client, admin_headers, client_headers):
    c = _create_client("inv_paydenied@example.com")
    invoice = _create_invoice(client, admin_headers, client_id=c.id).json()
    resp = client.post(
        f"/api/v1/invoices/{invoice['id']}/payments",
        json={"amount": "10.00", "method": "CASH"},
        headers=client_headers,
    )
    assert resp.status_code == 403


# --- edit restrictions ------------------------------------------------------


def test_paid_invoice_cannot_be_edited_except_notes(client, admin_headers):
    c = _create_client("inv_locked@example.com")
    invoice = _create_invoice(client, admin_headers, client_id=c.id, subtotal="100.00").json()
    client.post(
        f"/api/v1/invoices/{invoice['id']}/payments",
        json={"amount": "100.00", "method": "CASH"},
        headers=admin_headers,
    )

    blocked = client.patch(
        f"/api/v1/invoices/{invoice['id']}", json={"subtotal": "500.00"}, headers=admin_headers
    )
    assert blocked.status_code == 409

    allowed = client.patch(
        f"/api/v1/invoices/{invoice['id']}",
        json={"notes": "Paid in cash at the office"},
        headers=admin_headers,
    )
    assert allowed.status_code == 200
    assert allowed.json()["total"] == "100.00"


def test_cancelled_invoice_rejects_payments(client, admin_headers):
    c = _create_client("inv_cancelled@example.com")
    invoice = _create_invoice(client, admin_headers, client_id=c.id).json()
    client.patch(
        f"/api/v1/invoices/{invoice['id']}", json={"status": "CANCELLED"}, headers=admin_headers
    )
    resp = client.post(
        f"/api/v1/invoices/{invoice['id']}/payments",
        json={"amount": "10.00", "method": "CASH"},
        headers=admin_headers,
    )
    assert resp.status_code == 409


def test_patch_replaces_items_and_recomputes(client, admin_headers):
    c = _create_client("inv_repl@example.com")
    invoice = _create_invoice(
        client,
        admin_headers,
        client_id=c.id,
        items=[{"description": "A", "quantity": "1", "unit_price": "100.00"}],
    ).json()

    updated = client.patch(
        f"/api/v1/invoices/{invoice['id']}",
        json={"items": [{"description": "B", "quantity": "3", "unit_price": "50.00"}]},
        headers=admin_headers,
    ).json()
    assert len(updated["items"]) == 1
    assert updated["subtotal"] == "150.00"
    assert updated["total"] == "150.00"


# --- soft delete ------------------------------------------------------------


def test_soft_delete_hides_invoice_from_default_list(client, admin_headers):
    c = _create_client("inv_del@example.com")
    invoice = _create_invoice(client, admin_headers, client_id=c.id).json()

    deleted = client.delete(f"/api/v1/invoices/{invoice['id']}", headers=admin_headers)
    assert deleted.status_code == 200
    assert deleted.json()["is_active"] is False

    default_list = client.get("/api/v1/invoices", headers=admin_headers).json()
    assert invoice["id"] not in [i["id"] for i in default_list]

    with_inactive = client.get(
        "/api/v1/invoices", params={"include_inactive": True}, headers=admin_headers
    ).json()
    assert invoice["id"] in [i["id"] for i in with_inactive]


def test_staff_cannot_delete_invoice(client, admin_headers, staff_headers):
    c = _create_client("inv_staffdel@example.com")
    invoice = _create_invoice(client, admin_headers, client_id=c.id).json()
    resp = client.delete(f"/api/v1/invoices/{invoice['id']}", headers=staff_headers)
    assert resp.status_code == 403


# --- filters & search -------------------------------------------------------


def test_list_filters_by_status_client_and_search(client, admin_headers):
    c1 = _create_client("inv_f1@example.com")
    c2 = _create_client("inv_f2@example.com")
    a = _create_invoice(client, admin_headers, client_id=c1.id, status="SENT").json()
    _create_invoice(client, admin_headers, client_id=c2.id).json()

    by_client = client.get(
        "/api/v1/invoices", params={"client_id": c1.id}, headers=admin_headers
    ).json()
    assert [i["id"] for i in by_client] == [a["id"]]

    by_status = client.get(
        "/api/v1/invoices", params={"status": "SENT"}, headers=admin_headers
    ).json()
    assert [i["id"] for i in by_status] == [a["id"]]

    by_number = client.get(
        "/api/v1/invoices", params={"search": a["invoice_number"]}, headers=admin_headers
    ).json()
    assert [i["id"] for i in by_number] == [a["id"]]


# --- client scoping ---------------------------------------------------------


def test_client_sees_only_own_invoices(client, admin_headers):
    c1 = _create_client("inv_mine@example.com")
    c2 = _create_client("inv_theirs@example.com")
    mine = _create_invoice(client, admin_headers, client_id=c1.id).json()
    _create_invoice(client, admin_headers, client_id=c2.id).json()

    resp = client.get("/api/v1/client/invoices", headers=_client_auth_headers(c1))
    assert resp.status_code == 200
    assert [i["id"] for i in resp.json()] == [mine["id"]]


def test_client_cannot_read_another_clients_invoice(client, admin_headers):
    c1 = _create_client("inv_a@example.com")
    c2 = _create_client("inv_b@example.com")
    theirs = _create_invoice(client, admin_headers, client_id=c1.id).json()

    resp = client.get(f"/api/v1/client/invoices/{theirs['id']}", headers=_client_auth_headers(c2))
    assert resp.status_code == 404


def test_client_invoice_view_hides_staff_notes_and_shows_payments(client, admin_headers):
    c = _create_client("inv_notes@example.com")
    invoice = _create_invoice(
        client,
        admin_headers,
        client_id=c.id,
        subtotal="500.00",
        notes="Internal: chase this one",
    ).json()
    client.post(
        f"/api/v1/invoices/{invoice['id']}/payments",
        json={"amount": "200.00", "method": "MOBILE_MONEY", "reference": "MM-123", "notes": "internal"},
        headers=admin_headers,
    )

    body = client.get(
        f"/api/v1/client/invoices/{invoice['id']}", headers=_client_auth_headers(c)
    ).json()
    assert "notes" not in body
    assert body["balance_due"] == "300.00"
    assert body["status"] == "PARTIALLY_PAID"
    assert len(body["payments"]) == 1
    assert body["payments"][0]["reference"] == "MM-123"
    # The payment's internal note must not leak either.
    assert "notes" not in body["payments"][0]


def test_client_cannot_see_soft_deleted_invoice(client, admin_headers):
    c = _create_client("inv_cdel@example.com")
    invoice = _create_invoice(client, admin_headers, client_id=c.id).json()
    client.delete(f"/api/v1/invoices/{invoice['id']}", headers=admin_headers)

    listed = client.get("/api/v1/client/invoices", headers=_client_auth_headers(c)).json()
    assert listed == []
    single = client.get(
        f"/api/v1/client/invoices/{invoice['id']}", headers=_client_auth_headers(c)
    )
    assert single.status_code == 404


def test_client_standalone_invoice_is_visible(client, admin_headers):
    """No project anywhere in the chain — the client must still see it."""
    c = _create_client("inv_cstand@example.com")
    invoice = _create_invoice(client, admin_headers, client_id=c.id, subtotal="75.00").json()

    body = client.get(
        f"/api/v1/client/invoices/{invoice['id']}", headers=_client_auth_headers(c)
    ).json()
    assert body["project_id"] is None
    assert body["total"] == "75.00"


# --- dashboard integration --------------------------------------------------


def test_dashboard_reflects_real_invoice_numbers(client, admin_headers):
    c = _create_client("inv_dash@example.com")

    before = client.get("/api/v1/admin/dashboard", headers=admin_headers).json()
    assert before["invoices"] == {"pending": 0, "outstanding": "0.00"}

    # DRAFT invoices are not outstanding yet.
    _create_invoice(client, admin_headers, client_id=c.id, subtotal="1000.00")
    draft_only = client.get("/api/v1/admin/dashboard", headers=admin_headers).json()
    assert draft_only["invoices"]["pending"] == 0

    # A SENT invoice is outstanding for its full total...
    sent = _create_invoice(
        client, admin_headers, client_id=c.id, subtotal="1000.00", status="SENT"
    ).json()
    # ...and a part-paid one only for its remaining balance.
    partial = _create_invoice(
        client, admin_headers, client_id=c.id, subtotal="500.00", status="SENT"
    ).json()
    client.post(
        f"/api/v1/invoices/{partial['id']}/payments",
        json={"amount": "200.00", "method": "CASH"},
        headers=admin_headers,
    )

    stats = client.get("/api/v1/admin/dashboard", headers=admin_headers).json()
    assert stats["invoices"]["pending"] == 2
    assert stats["invoices"]["outstanding"] == "1300.00"  # 1000 + (500 - 200)

    # Soft-deleted invoices drop out of the figures.
    client.delete(f"/api/v1/invoices/{sent['id']}", headers=admin_headers)
    after_delete = client.get("/api/v1/admin/dashboard", headers=admin_headers).json()
    assert after_delete["invoices"]["pending"] == 1
    assert after_delete["invoices"]["outstanding"] == "300.00"


def test_dashboard_shape_is_unchanged(client, admin_headers):
    """The existing keys must all still be there — only values changed."""
    body = client.get("/api/v1/admin/dashboard", headers=admin_headers).json()
    assert set(body) == {
        "users",
        "services",
        "projects",
        "quotes",
        "invoices",
        "hosting",
        "store",
        "support",
    }


# --- VAT (18%) --------------------------------------------------------------


def test_vat_rate_computes_tax_and_total(client, admin_headers):
    c = _create_client("inv_vat_basic@example.com")
    resp = _create_invoice(client, admin_headers, client_id=c.id, subtotal="1000.00", tax_rate="18")
    assert resp.status_code == 201
    body = resp.json()
    assert body["tax_rate"] == "18.00"
    assert body["tax"] == "180.00"
    assert body["total"] == "1180.00"


def test_vat_applies_after_discount_line(client, admin_headers):
    """VAT is charged on the subtotal; the discount comes off the total."""
    c = _create_client("inv_vat_discount@example.com")
    body = _create_invoice(
        client, admin_headers, client_id=c.id, subtotal="1000.00", tax_rate="18", discount="100.00"
    ).json()
    assert body["tax"] == "180.00"
    # 1000 + 180 - 100
    assert body["total"] == "1080.00"


def test_vat_ignores_a_client_supplied_tax_amount(client, admin_headers):
    """A rate is authoritative — a forged tax amount must not survive."""
    c = _create_client("inv_vat_forge@example.com")
    body = _create_invoice(
        client, admin_headers, client_id=c.id, subtotal="1000.00", tax_rate="18", tax="1.00"
    ).json()
    assert body["tax"] == "180.00"
    assert body["total"] == "1180.00"


def test_vat_recomputes_when_line_items_change(client, admin_headers):
    c = _create_client("inv_vat_items@example.com")
    invoice = _create_invoice(
        client,
        admin_headers,
        client_id=c.id,
        tax_rate="18",
        items=[{"description": "Build", "quantity": "1", "unit_price": "1000.00"}],
    ).json()
    assert invoice["subtotal"] == "1000.00"
    assert invoice["tax"] == "180.00"

    updated = client.patch(
        f"/api/v1/invoices/{invoice['id']}",
        json={"items": [{"description": "Build", "quantity": "2", "unit_price": "1000.00"}]},
        headers=admin_headers,
    ).json()
    assert updated["subtotal"] == "2000.00"
    assert updated["tax"] == "360.00"
    assert updated["total"] == "2360.00"


def test_manual_tax_path_is_unchanged_without_a_rate(client, admin_headers):
    """The pre-VAT behaviour: no rate, tax is exactly what was typed."""
    c = _create_client("inv_manual_tax@example.com")
    body = _create_invoice(
        client, admin_headers, client_id=c.id, subtotal="1000.00", tax="55.00"
    ).json()
    assert body["tax_rate"] is None
    assert body["tax"] == "55.00"
    assert body["total"] == "1055.00"

    # Editing line items leaves a manual amount alone.
    updated = client.patch(
        f"/api/v1/invoices/{body['id']}",
        json={"items": [{"description": "Work", "quantity": "1", "unit_price": "400.00"}]},
        headers=admin_headers,
    ).json()
    assert updated["tax_rate"] is None
    assert updated["tax"] == "55.00"
    assert updated["total"] == "455.00"


def test_no_tax_at_all_still_works(client, admin_headers):
    c = _create_client("inv_no_tax@example.com")
    body = _create_invoice(client, admin_headers, client_id=c.id, subtotal="800.00").json()
    assert body["tax_rate"] is None
    assert body["tax"] is None
    assert body["total"] == "800.00"


def test_switching_between_vat_and_manual_modes(client, admin_headers):
    c = _create_client("inv_vat_toggle@example.com")
    invoice = _create_invoice(client, admin_headers, client_id=c.id, subtotal="1000.00").json()
    assert invoice["tax_rate"] is None

    # Manual -> VAT
    on = client.patch(
        f"/api/v1/invoices/{invoice['id']}", json={"tax_rate": "18"}, headers=admin_headers
    ).json()
    assert on["tax"] == "180.00"
    assert on["total"] == "1180.00"

    # VAT -> manual: an explicit null hands control back to the typed amount.
    off = client.patch(
        f"/api/v1/invoices/{invoice['id']}",
        json={"tax_rate": None, "tax": "20.00"},
        headers=admin_headers,
    ).json()
    assert off["tax_rate"] is None
    assert off["tax"] == "20.00"
    assert off["total"] == "1020.00"


def test_client_invoice_view_shows_vat_rate_and_amount(client, admin_headers):
    """VAT is a charge the client pays, so it must be visible to them."""
    c = _create_client("inv_vat_client@example.com")
    invoice = _create_invoice(
        client,
        admin_headers,
        client_id=c.id,
        subtotal="1000.00",
        tax_rate="18",
        status="SENT",
        notes="internal only",
    ).json()

    body = client.get(
        f"/api/v1/client/invoices/{invoice['id']}", headers=_client_auth_headers(c)
    ).json()
    assert body["tax_rate"] == "18.00"
    assert body["tax"] == "180.00"
    assert body["total"] == "1180.00"
    # Staff notes stay hidden even though VAT is now exposed.
    assert "notes" not in body


def test_vat_rate_is_validated(client, admin_headers):
    c = _create_client("inv_vat_invalid@example.com")
    over = _create_invoice(client, admin_headers, client_id=c.id, tax_rate="150")
    assert over.status_code == 422
    negative = _create_invoice(client, admin_headers, client_id=c.id, tax_rate="-5")
    assert negative.status_code == 422


def test_vat_half_cent_rounds_up_not_to_even(client, admin_headers):
    """
    RRA expects half-up rounding on VAT. 1000.25 x 18% is exactly 180.045 —
    a half-cent tie. Half-up gives 180.05; Python's default banker's rounding
    would give 180.04, which is what this guards against.
    """
    c = _create_client("inv_vat_rounding@example.com")
    body = _create_invoice(
        client, admin_headers, client_id=c.id, subtotal="1000.25", tax_rate="18"
    ).json()
    assert body["tax"] == "180.05"
    assert body["total"] == "1180.30"


def test_vat_rounding_ties_always_go_up(client, admin_headers):
    """
    Both parities of the preceding digit must round up — that is the difference
    between half-up and half-even, which only diverges on one of them.
    """
    c = _create_client("inv_vat_rounding2@example.com")

    # 1000.75 x 18% = 180.135 -> 180.14 under both modes (3 is odd).
    odd = _create_invoice(
        client, admin_headers, client_id=c.id, subtotal="1000.75", tax_rate="18"
    ).json()
    assert odd["tax"] == "180.14"

    # 1000.25 x 18% = 180.045 -> half-up 180.05, half-even would be 180.04.
    even = _create_invoice(
        client, admin_headers, client_id=c.id, subtotal="1000.25", tax_rate="18"
    ).json()
    assert even["tax"] == "180.05"


def test_vat_rounding_survives_a_line_item_edit(client, admin_headers):
    """The half-up rule applies on recompute, not just on create."""
    c = _create_client("inv_vat_rounding3@example.com")
    invoice = _create_invoice(
        client,
        admin_headers,
        client_id=c.id,
        tax_rate="18",
        items=[{"description": "Service", "quantity": "1", "unit_price": "500.00"}],
    ).json()
    assert invoice["tax"] == "90.00"

    updated = client.patch(
        f"/api/v1/invoices/{invoice['id']}",
        json={
            "tax_rate": "18",
            "items": [{"description": "Service", "quantity": "1", "unit_price": "1000.25"}],
        },
        headers=admin_headers,
    ).json()
    assert updated["subtotal"] == "1000.25"
    assert updated["tax"] == "180.05"
    assert updated["total"] == "1180.30"

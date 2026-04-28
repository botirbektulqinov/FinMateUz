from datetime import date
from decimal import Decimal

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_token
from app.enums import AuditAction, TransactionSource, TransactionStatus, TransactionType
from app.models import AuditLog, User
from app.schemas import TransactionCreate, TransactionUpdate
from app.services.reports import category_breakdown, overview_report
from app.services.transactions import approve_transaction, create_transaction, delete_transaction, list_transactions, update_transaction


def auth_headers(user: User, company_id: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_token(user.id, 'access')}", "X-Company-Id": company_id}


def tx_payload(category_id: str, amount: str, tx_type: TransactionType = TransactionType.expense) -> TransactionCreate:
    return TransactionCreate(
        type=tx_type,
        amount=Decimal(amount),
        category_id=category_id,
        transaction_date=date(2026, 4, 27),
        note="test transaction",
        source=TransactionSource.dashboard,
    )


def test_operator_transaction_starts_pending_and_is_excluded_until_approved(db: Session, company_setup) -> None:
    operator_ctx = company_setup["operator_ctx"]
    owner_ctx = company_setup["owner_ctx"]
    logistics = company_setup["categories"]["Logistics"]

    tx = create_transaction(db, operator_ctx, tx_payload(logistics.id, "250000"))

    assert tx.status == TransactionStatus.pending
    report = overview_report(db, owner_ctx, today=date(2026, 4, 27))
    assert report.summary.month_expenses == Decimal("0")
    assert report.summary.pending_approval_count == 1

    approved = approve_transaction(db, owner_ctx, tx.id, approve=True)

    assert approved.status == TransactionStatus.confirmed
    report = overview_report(db, owner_ctx, today=date(2026, 4, 27))
    assert report.summary.month_expenses == Decimal("250000.00")


def test_company_isolation_in_transaction_queries(db: Session, company_setup) -> None:
    owner_ctx = company_setup["owner_ctx"]
    other_ctx = company_setup["other_ctx"]
    sales = company_setup["categories"]["Sales"]
    other_sales = company_setup["other_categories"]["Sales"]

    create_transaction(db, owner_ctx, tx_payload(sales.id, "1000000", TransactionType.income))
    create_transaction(db, other_ctx, tx_payload(other_sales.id, "3000000", TransactionType.income))

    items, total = list_transactions(db, owner_ctx)

    assert total == 1
    assert len(items) == 1
    assert items[0].company_id == owner_ctx.company_id


def test_viewer_cannot_create_and_operator_cannot_delete_confirmed(db: Session, company_setup) -> None:
    owner_ctx = company_setup["owner_ctx"]
    viewer_ctx = company_setup["viewer_ctx"]
    operator_ctx = company_setup["operator_ctx"]
    logistics = company_setup["categories"]["Logistics"]

    with pytest.raises(HTTPException):
        create_transaction(db, viewer_ctx, tx_payload(logistics.id, "10000"))

    tx = create_transaction(db, owner_ctx, tx_payload(logistics.id, "10000"))
    with pytest.raises(HTTPException):
        delete_transaction(db, operator_ctx, tx.id)


def test_operator_can_edit_own_pending_but_not_after_approval(db: Session, company_setup) -> None:
    operator_ctx = company_setup["operator_ctx"]
    owner_ctx = company_setup["owner_ctx"]
    logistics = company_setup["categories"]["Logistics"]
    tx = create_transaction(db, operator_ctx, tx_payload(logistics.id, "10000"))

    updated = update_transaction(db, operator_ctx, tx.id, TransactionUpdate(amount=Decimal("12000")))
    assert updated.amount == Decimal("12000.00")

    approve_transaction(db, owner_ctx, tx.id, approve=True)
    with pytest.raises(HTTPException) as exc:
        update_transaction(db, operator_ctx, tx.id, TransactionUpdate(amount=Decimal("14000")))
    assert exc.value.status_code == 403


def test_viewer_cannot_delete_pending_transaction(db: Session, company_setup) -> None:
    operator_ctx = company_setup["operator_ctx"]
    viewer_ctx = company_setup["viewer_ctx"]
    logistics = company_setup["categories"]["Logistics"]
    tx = create_transaction(db, operator_ctx, tx_payload(logistics.id, "10000"))

    with pytest.raises(HTTPException) as exc:
        delete_transaction(db, viewer_ctx, tx.id)
    assert exc.value.status_code == 403


def test_soft_delete_removes_confirmed_transaction_from_default_lists(db: Session, company_setup) -> None:
    owner_ctx = company_setup["owner_ctx"]
    logistics = company_setup["categories"]["Logistics"]
    tx = create_transaction(db, owner_ctx, tx_payload(logistics.id, "10000"))

    delete_transaction(db, owner_ctx, tx.id)
    items, total = list_transactions(db, owner_ctx)

    assert total == 0
    assert items == []


def test_category_type_mismatch_rejected(db: Session, company_setup) -> None:
    owner_ctx = company_setup["owner_ctx"]
    logistics = company_setup["categories"]["Logistics"]
    with pytest.raises(HTTPException) as exc:
        create_transaction(db, owner_ctx, tx_payload(logistics.id, "1000000", TransactionType.income))
    assert exc.value.status_code == 422


def test_transaction_list_filters(db: Session, company_setup) -> None:
    owner_ctx = company_setup["owner_ctx"]
    logistics = company_setup["categories"]["Logistics"]
    sales = company_setup["categories"]["Sales"]
    create_transaction(db, owner_ctx, tx_payload(logistics.id, "120000", TransactionType.expense))
    create_transaction(db, owner_ctx, tx_payload(sales.id, "900000", TransactionType.income))

    items, total = list_transactions(db, owner_ctx, tx_type=TransactionType.expense, search="test")

    assert total == 1
    assert items[0].type == TransactionType.expense
    assert items[0].category_id == logistics.id


def test_overview_and_category_breakdown_calculations(db: Session, company_setup) -> None:
    owner_ctx = company_setup["owner_ctx"]
    operator_ctx = company_setup["operator_ctx"]
    sales = company_setup["categories"]["Sales"]
    logistics = company_setup["categories"]["Logistics"]
    rent = company_setup["categories"]["Rent"]
    deleted = create_transaction(db, owner_ctx, tx_payload(logistics.id, "10000", TransactionType.expense))
    create_transaction(db, owner_ctx, tx_payload(sales.id, "1000000", TransactionType.income))
    create_transaction(db, owner_ctx, tx_payload(logistics.id, "250000", TransactionType.expense))
    create_transaction(db, owner_ctx, tx_payload(rent.id, "150000", TransactionType.expense))
    create_transaction(db, operator_ctx, tx_payload(logistics.id, "999999", TransactionType.expense))
    delete_transaction(db, owner_ctx, deleted.id)

    report = overview_report(db, owner_ctx, today=date(2026, 4, 27))
    breakdown = category_breakdown(db, owner_ctx, TransactionType.expense, date(2026, 4, 1), date(2026, 4, 30))

    assert report.summary.month_income == Decimal("1000000.00")
    assert report.summary.month_expenses == Decimal("400000.00")
    assert report.summary.net_cash_flow == Decimal("600000.00")
    assert report.summary.pending_approval_count == 1
    assert [(item.category_name, item.total) for item in breakdown] == [
        ("Logistics", Decimal("250000.00")),
        ("Rent", Decimal("150000.00")),
    ]


def test_register_login_refresh_and_me(client: TestClient) -> None:
    payload = {
        "email": "new-owner@example.com",
        "full_name": "New Owner",
        "password": "Password123",
        "company_name": "New Company LLC",
        "business_type": "Retail",
    }
    register_response = client.post("/api/v1/auth/register", json=payload)
    assert register_response.status_code == 201
    tokens = register_response.json()
    assert tokens["access_token"]

    login_response = client.post("/api/v1/auth/login", json={"email": payload["email"], "password": payload["password"]})
    assert login_response.status_code == 200
    refresh_response = client.post("/api/v1/auth/refresh", json={"refresh_token": login_response.json()["refresh_token"]})
    assert refresh_response.status_code == 200
    me_response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert me_response.status_code == 200
    assert me_response.json()["email"] == payload["email"]


def test_telegram_link_flow(client: TestClient, company_setup) -> None:
    company = company_setup["company"]
    owner = company_setup["owner"]
    headers = auth_headers(owner, company.id)

    code_response = client.get("/api/v1/bot/link-code", headers=headers)
    assert code_response.status_code == 200
    command = code_response.json()["command"]
    assert command.startswith("/link ")

    link_response = client.post(
        "/api/v1/bot/link",
        headers={"X-Bot-Api-Token": "local-bot-token"},
        json={"telegram_user_id": 6572793464, "link_code": code_response.json()["link_code"]},
    )
    assert link_response.status_code == 200
    assert link_response.json()["company_id"] == company.id

    account_response = client.get(
        "/api/v1/bot/telegram-accounts/6572793464",
        headers={"X-Bot-Api-Token": "local-bot-token"},
    )
    assert account_response.status_code == 200
    assert account_response.json()["company_id"] == company.id
    assert account_response.json()["access_token"]


def test_transaction_api_validation_and_rbac(client: TestClient, company_setup) -> None:
    company = company_setup["company"]
    owner = company_setup["owner"]
    viewer = company_setup["viewer"]
    logistics = company_setup["categories"]["Logistics"]
    sales = company_setup["categories"]["Sales"]
    owner_headers = auth_headers(owner, company.id)
    viewer_headers = auth_headers(viewer, company.id)

    invalid_amount = client.post(
        "/api/v1/transactions",
        json={
            "type": "expense",
            "amount": "-1",
            "category_id": logistics.id,
            "transaction_date": "2026-04-27",
            "source": "dashboard",
        },
        headers=owner_headers,
    )
    assert invalid_amount.status_code == 422

    mismatch = client.post(
        "/api/v1/transactions",
        json={
            "type": "income",
            "amount": "100000",
            "category_id": logistics.id,
            "transaction_date": "2026-04-27",
            "source": "dashboard",
        },
        headers=owner_headers,
    )
    assert mismatch.status_code == 422

    forbidden = client.post(
        "/api/v1/transactions",
        json={
            "type": "income",
            "amount": "100000",
            "category_id": sales.id,
            "transaction_date": "2026-04-27",
            "source": "dashboard",
        },
        headers=viewer_headers,
    )
    assert forbidden.status_code == 403


def test_operator_pending_transaction_api_approval(client: TestClient, company_setup) -> None:
    company = company_setup["company"]
    owner = company_setup["owner"]
    operator = company_setup["operator"]
    logistics = company_setup["categories"]["Logistics"]

    create_response = client.post(
        "/api/v1/transactions",
        json={
            "type": "expense",
            "amount": "50000",
            "category_id": logistics.id,
            "transaction_date": "2026-04-27",
            "source": "dashboard",
        },
        headers=auth_headers(operator, company.id),
    )
    assert create_response.status_code == 201
    tx = create_response.json()
    assert tx["status"] == "pending"

    approve_response = client.post(
        f"/api/v1/transactions/{tx['id']}/approve",
        headers=auth_headers(owner, company.id),
    )
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "confirmed"


def test_company_isolation_api_denies_cross_company_header(client: TestClient, company_setup) -> None:
    owner = company_setup["owner"]
    other_company = company_setup["other_company"]
    response = client.get("/api/v1/transactions", headers=auth_headers(owner, other_company.id))
    assert response.status_code == 403


def test_report_endpoints_use_confirmed_transactions_by_default(client: TestClient, company_setup) -> None:
    company = company_setup["company"]
    owner = company_setup["owner"]
    operator = company_setup["operator"]
    sales = company_setup["categories"]["Sales"]
    logistics = company_setup["categories"]["Logistics"]
    owner_headers = auth_headers(owner, company.id)

    client.post(
        "/api/v1/transactions",
        json={"type": "income", "amount": "500000", "category_id": sales.id, "transaction_date": "2026-04-27"},
        headers=owner_headers,
    )
    client.post(
        "/api/v1/transactions",
        json={"type": "expense", "amount": "200000", "category_id": logistics.id, "transaction_date": "2026-04-27"},
        headers=owner_headers,
    )
    client.post(
        "/api/v1/transactions",
        json={"type": "expense", "amount": "999000", "category_id": logistics.id, "transaction_date": "2026-04-27"},
        headers=auth_headers(operator, company.id),
    )

    overview = client.get("/api/v1/reports/overview?today=2026-04-27", headers=owner_headers)
    breakdown = client.get("/api/v1/reports/category-breakdown?type=expense&start_date=2026-04-01&end_date=2026-04-30", headers=owner_headers)

    assert overview.status_code == 200
    assert overview.json()["summary"]["month_income"] == "500000.00"
    assert overview.json()["summary"]["month_expenses"] == "200000.00"
    assert overview.json()["summary"]["pending_approval_count"] == 1
    assert breakdown.status_code == 200
    assert breakdown.json()[0]["total"] == "200000.00"


def test_reports_can_include_pending_when_requested(client: TestClient, company_setup) -> None:
    company = company_setup["company"]
    owner = company_setup["owner"]
    operator = company_setup["operator"]
    logistics = company_setup["categories"]["Logistics"]
    client.post(
        "/api/v1/transactions",
        json={"type": "expense", "amount": "300000", "category_id": logistics.id, "transaction_date": "2026-04-27"},
        headers=auth_headers(operator, company.id),
    )

    default_report = client.get("/api/v1/reports/overview?today=2026-04-27", headers=auth_headers(owner, company.id))
    pending_report = client.get(
        "/api/v1/reports/overview?today=2026-04-27&include_pending=true",
        headers=auth_headers(owner, company.id),
    )

    assert default_report.json()["summary"]["month_expenses"] == "0.00"
    assert pending_report.json()["summary"]["month_expenses"] == "300000.00"


def test_transaction_audit_logs_are_recorded(db: Session, company_setup) -> None:
    owner_ctx = company_setup["owner_ctx"]
    logistics = company_setup["categories"]["Logistics"]
    tx = create_transaction(db, owner_ctx, tx_payload(logistics.id, "10000"))
    update_transaction(db, owner_ctx, tx.id, TransactionUpdate(note="corrected note"))
    delete_transaction(db, owner_ctx, tx.id)

    actions = [row.action for row in db.query(AuditLog).filter(AuditLog.company_id == owner_ctx.company_id).all()]
    assert AuditAction.transaction_create in actions
    assert AuditAction.transaction_update in actions
    assert AuditAction.transaction_delete in actions

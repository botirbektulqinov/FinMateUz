from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.core.security import create_token
from app.db import Base, get_db
from app.enums import Role
from app.main import app
from app.models import Category, Company, CompanyMember, User
from app.services.categories import create_default_categories
from app.services.permissions import MembershipContext


@pytest.fixture()
def db() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture()
def client(db: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def company_setup(db: Session):
    owner = User(email="owner@example.com", full_name="Owner", hashed_password=hash_password("password123"))
    operator = User(email="operator@example.com", full_name="Operator", hashed_password=hash_password("password123"))
    viewer = User(email="viewer@example.com", full_name="Viewer", hashed_password=hash_password("password123"))
    other_owner = User(email="other@example.com", full_name="Other", hashed_password=hash_password("password123"))
    company = Company(name="Test Company LLC", business_type="Retail")
    other_company = Company(name="Other LLC", business_type="Services")
    db.add_all([owner, operator, viewer, other_owner, company, other_company])
    db.flush()
    owner_member = CompanyMember(company_id=company.id, user_id=owner.id, role=Role.owner)
    operator_member = CompanyMember(company_id=company.id, user_id=operator.id, role=Role.operator)
    viewer_member = CompanyMember(company_id=company.id, user_id=viewer.id, role=Role.viewer)
    other_member = CompanyMember(company_id=other_company.id, user_id=other_owner.id, role=Role.owner)
    db.add_all([owner_member, operator_member, viewer_member, other_member])
    create_default_categories(db, company.id)
    create_default_categories(db, other_company.id)
    db.commit()
    categories = {
        item.name: item
        for item in db.query(Category).filter(Category.company_id == company.id, Category.deleted_at.is_(None)).all()
    }
    other_categories = {
        item.name: item
        for item in db.query(Category).filter(Category.company_id == other_company.id, Category.deleted_at.is_(None)).all()
    }
    return {
        "owner": owner,
        "operator": operator,
        "viewer": viewer,
        "other_owner": other_owner,
        "company": company,
        "other_company": other_company,
        "owner_ctx": MembershipContext(user=owner, member=owner_member),
        "operator_ctx": MembershipContext(user=operator, member=operator_member),
        "viewer_ctx": MembershipContext(user=viewer, member=viewer_member),
        "other_ctx": MembershipContext(user=other_owner, member=other_member),
        "categories": categories,
        "other_categories": other_categories,
    }


def auth_headers(user: User, company_id: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_token(user.id, 'access')}", "X-Company-Id": company_id}

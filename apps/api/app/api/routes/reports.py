from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_company_context
from app.enums import TransactionType
from app.schemas import CategoryBreakdownPoint, DashboardReport, OverviewReport, TimeSeriesPoint
from app.services.permissions import MembershipContext
from app.services import reports as service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/overview", response_model=OverviewReport)
def overview(
    today: date | None = None,
    include_pending: bool = False,
    ctx: MembershipContext = Depends(get_company_context),
    db: Session = Depends(get_db),
) -> OverviewReport:
    return service.overview_report(db, ctx, today=today, include_pending=include_pending)


@router.get("/cash-flow", response_model=list[TimeSeriesPoint])
def cash_flow(
    include_pending: bool = False,
    ctx: MembershipContext = Depends(get_company_context),
    db: Session = Depends(get_db),
) -> list[TimeSeriesPoint]:
    return service.cash_flow(db, ctx, include_pending=include_pending)


@router.get("/category-breakdown", response_model=list[CategoryBreakdownPoint])
def category_breakdown(
    type: TransactionType,
    start_date: date | None = None,
    end_date: date | None = None,
    include_pending: bool = False,
    ctx: MembershipContext = Depends(get_company_context),
    db: Session = Depends(get_db),
) -> list[CategoryBreakdownPoint]:
    return service.category_breakdown(db, ctx, type, start_date, end_date, include_pending=include_pending)


@router.get("/top-categories", response_model=list[CategoryBreakdownPoint])
def top_categories(
    type: TransactionType,
    limit: int = 5,
    include_pending: bool = False,
    ctx: MembershipContext = Depends(get_company_context),
    db: Session = Depends(get_db),
) -> list[CategoryBreakdownPoint]:
    return service.top_categories(db, ctx, type, limit=limit, include_pending=include_pending)


@router.get("/dashboard", response_model=DashboardReport)
def dashboard(ctx: MembershipContext = Depends(get_company_context), db: Session = Depends(get_db)) -> DashboardReport:
    return service.dashboard_report(db, ctx)

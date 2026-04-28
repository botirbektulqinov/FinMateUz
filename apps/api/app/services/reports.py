from collections import defaultdict
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.enums import TransactionStatus, TransactionType
from app.models import Category, Transaction
from app.schemas import CategoryBreakdownPoint, DashboardReport, OverviewReport, ReportSummary, TimeSeriesPoint
from app.services.permissions import MembershipContext
from app.services.transactions import list_transactions, to_read


def _month_bounds(today: date) -> tuple[date, date, date, date]:
    start = today.replace(day=1)
    previous_end = start.replace(day=1).fromordinal(start.toordinal() - 1)
    previous_start = previous_end.replace(day=1)
    return start, today, previous_start, previous_end


def _statuses(include_pending: bool = False) -> list[TransactionStatus]:
    statuses = [TransactionStatus.confirmed]
    if include_pending:
        statuses.append(TransactionStatus.pending)
    return statuses


def _sum_for(
    db: Session,
    company_id: str,
    tx_type: TransactionType,
    start: date,
    end: date,
    include_pending: bool = False,
) -> Decimal:
    value = db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.company_id == company_id,
            Transaction.type == tx_type,
            Transaction.status.in_(_statuses(include_pending)),
            Transaction.transaction_date >= start,
            Transaction.transaction_date <= end,
        )
    ).scalar_one()
    return Decimal(value)


def _percent_change(current: Decimal, previous: Decimal) -> Decimal | None:
    if previous == 0:
        return None
    return ((current - previous) / previous * Decimal("100")).quantize(Decimal("0.01"))


def overview_report(
    db: Session, ctx: MembershipContext, today: date | None = None, include_pending: bool = False
) -> OverviewReport:
    today = today or date.today()
    month_start, month_end, previous_start, previous_end = _month_bounds(today)
    income = _sum_for(db, ctx.company_id, TransactionType.income, month_start, month_end, include_pending)
    expenses = _sum_for(db, ctx.company_id, TransactionType.expense, month_start, month_end, include_pending)
    prev_income = _sum_for(db, ctx.company_id, TransactionType.income, previous_start, previous_end, include_pending)
    prev_expenses = _sum_for(db, ctx.company_id, TransactionType.expense, previous_start, previous_end, include_pending)
    pending_count = db.execute(
        select(func.count(Transaction.id)).where(
            Transaction.company_id == ctx.company_id, Transaction.status == TransactionStatus.pending
        )
    ).scalar_one()
    recent, _ = list_transactions(db, ctx, limit=8)
    return OverviewReport(
        summary=ReportSummary(
            month_income=income,
            month_expenses=expenses,
            net_cash_flow=income - expenses,
            previous_month_income=prev_income,
            previous_month_expenses=prev_expenses,
            income_change_percent=_percent_change(income, prev_income),
            expense_change_percent=_percent_change(expenses, prev_expenses),
            pending_approval_count=pending_count,
        ),
        recent_transactions=[to_read(item) for item in recent],
    )


def dashboard_report(db: Session, ctx: MembershipContext, today: date | None = None) -> DashboardReport:
    today = today or date.today()
    month_start, month_end, _, _ = _month_bounds(today)
    overview = overview_report(db, ctx, today=today)
    series = cash_flow(db, ctx)
    expense_breakdown = category_breakdown(db, ctx, TransactionType.expense, month_start, month_end)
    income_breakdown = category_breakdown(db, ctx, TransactionType.income, month_start, month_end)
    return DashboardReport(
        summary=overview.summary,
        income_vs_expenses=series,
        expense_breakdown=expense_breakdown,
        income_breakdown=income_breakdown,
        top_expense_categories=expense_breakdown[:5],
        top_income_categories=income_breakdown[:5],
        recent_transactions=overview.recent_transactions,
    )


def cash_flow(db: Session, ctx: MembershipContext, include_pending: bool = False) -> list[TimeSeriesPoint]:
    rows = db.execute(
        select(Transaction.transaction_date, Transaction.type, func.sum(Transaction.amount))
        .where(Transaction.company_id == ctx.company_id, Transaction.status.in_(_statuses(include_pending)))
        .group_by(Transaction.transaction_date, Transaction.type)
        .order_by(Transaction.transaction_date)
    ).all()
    buckets: dict[str, dict[str, Decimal]] = defaultdict(lambda: {"income": Decimal("0"), "expense": Decimal("0")})
    for tx_date, tx_type, total in rows:
        key = tx_date.strftime("%Y-%m")
        buckets[key][str(tx_type)] += Decimal(total)
    return [
        TimeSeriesPoint(period=period, income=values["income"], expense=values["expense"], net=values["income"] - values["expense"])
        for period, values in buckets.items()
    ]


def category_breakdown(
    db: Session,
    ctx: MembershipContext,
    tx_type: TransactionType,
    start: date | None = None,
    end: date | None = None,
    include_pending: bool = False,
) -> list[CategoryBreakdownPoint]:
    query = (
        select(Category.id, Category.name, func.sum(Transaction.amount).label("total"))
        .join(Transaction, Transaction.category_id == Category.id)
        .where(
            Transaction.company_id == ctx.company_id,
            Transaction.type == tx_type,
            Transaction.status.in_(_statuses(include_pending)),
        )
    )
    if start:
        query = query.where(Transaction.transaction_date >= start)
    if end:
        query = query.where(Transaction.transaction_date <= end)
    rows = db.execute(query.group_by(Category.id, Category.name).order_by(func.sum(Transaction.amount).desc())).all()
    return [CategoryBreakdownPoint(category_id=row[0], category_name=row[1], total=Decimal(row[2])) for row in rows]


def top_categories(
    db: Session,
    ctx: MembershipContext,
    tx_type: TransactionType,
    limit: int = 5,
    include_pending: bool = False,
) -> list[CategoryBreakdownPoint]:
    return category_breakdown(db, ctx, tx_type, include_pending=include_pending)[:limit]

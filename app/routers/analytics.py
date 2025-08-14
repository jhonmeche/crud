from __future__ import annotations
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlmodel import Session, select

from app.database import get_session
from app.models import WorkOrder, WorkOrderEvent


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/")
def analytics_summary(session: Session = Depends(get_session)) -> Dict[str, Any]:
    """Return basic analytics information about work orders."""

    total_orders = session.exec(select(func.count(WorkOrder.id))).one()

    # Orders grouped by status and month (YYYY-MM)
    stmt = (
        select(
            func.strftime("%Y-%m", WorkOrder.created_at).label("month"),
            WorkOrder.status,
            func.count(WorkOrder.id).label("count"),
        )
        .group_by("month", WorkOrder.status)
        .order_by("month")
    )
    status_month_rows = session.exec(stmt).all()
    orders_by_status: List[Dict[str, Any]] = [
        {"month": month, "status": status, "count": count}
        for month, status, count in status_month_rows
    ]

    # Average time from creation to first delivered event (in seconds)
    delivered_rows = session.exec(
        select(WorkOrder.created_at, WorkOrderEvent.created_at)
        .join(WorkOrderEvent, WorkOrderEvent.work_order_id == WorkOrder.id)
        .where(WorkOrderEvent.status == "entregado")
    ).all()
    avg_seconds: Optional[float] = None
    if delivered_rows:
        durations = [
            (delivered_at - created_at).total_seconds()
            for created_at, delivered_at in delivered_rows
        ]
        avg_seconds = sum(durations) / len(durations)

    return {
        "total_orders": total_orders,
        "orders_by_status": orders_by_status,
        "avg_time_to_delivered_seconds": avg_seconds,
    }


from __future__ import annotations

import time
from functools import lru_cache
from typing import Dict

from sqlalchemy import func
from sqlmodel import Session, select

from .database import engine
from .models import WorkOrder

CACHE_TTL_SECONDS = 300  # 5 minutes


def _cache_key() -> int:
    """Return a time-based cache key that changes every TTL interval."""
    return int(time.time() // CACHE_TTL_SECONDS)


@lru_cache(maxsize=1)
def _status_counts_cached(_: int) -> Dict[str, int]:
    """Internal cached function computing order status counts."""
    with Session(engine) as session:
        rows = session.exec(
            select(WorkOrder.status, func.count(WorkOrder.id)).group_by(WorkOrder.status)
        ).all()
    return {status: count for status, count in rows}


def get_order_status_counts() -> Dict[str, int]:
    """Return cached order counts grouped by status."""
    return _status_counts_cached(_cache_key())


def invalidate_cache() -> None:
    """Clear analytics cache."""
    _status_counts_cached.cache_clear()

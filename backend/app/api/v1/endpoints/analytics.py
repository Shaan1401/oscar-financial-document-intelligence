from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional

from app.database.session import get_db
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Financial Analytics"])

@router.get("/summary")
def get_summary_metrics(db: Session = Depends(get_db)):
    """Returns database-backed portfolio KPIs and summary statistics."""
    return AnalyticsService.get_summary(db)

@router.get("/categories")
def get_category_breakdown(
    statement_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Returns category-wise spend, income, and percentage distributions."""
    return AnalyticsService.get_category_analytics(db, statement_id=statement_id)

@router.get("/cashflow")
def get_cashflow_timeline(
    statement_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Returns daily/monthly cashflow inflows and outflows timeline."""
    return AnalyticsService.get_cashflow(db, statement_id=statement_id)

@router.get("/distribution")
def get_classification_distribution(db: Session = Depends(get_db)):
    """Returns transaction counts and percentages grouped by classification method."""
    return AnalyticsService.get_classification_distribution(db)


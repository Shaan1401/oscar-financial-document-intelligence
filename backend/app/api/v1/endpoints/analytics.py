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

@router.get("/running-balance")
def get_running_balance(
    statement_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Returns step-by-step transaction running balance trajectory and anomaly flags."""
    return AnalyticsService.get_running_balance_trajectory(db, statement_id=statement_id)

@router.get("/activity-heatmap")
def get_activity_heatmap(
    statement_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Returns daily transaction counts and monetary volume for calendar heatmaps."""
    return AnalyticsService.get_activity_heatmap(db, statement_id=statement_id)

@router.get("/merchants")
def get_merchant_concentration(
    statement_id: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Returns merchant spend concentration and cumulative Pareto share."""
    return AnalyticsService.get_merchant_concentration(db, statement_id=statement_id, limit=limit)

@router.get("/channels")
def get_payment_channels(
    statement_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Returns transaction distribution by payment channel (UPI, NEFT, IMPS, Card, ATM, etc)."""
    return AnalyticsService.get_payment_channels(db, statement_id=statement_id)

@router.get("/classification-deep")
def get_classification_deep(db: Session = Depends(get_db)):
    """Returns detailed classification counts, rule conflict audits, and confidence score distribution."""
    return AnalyticsService.get_classification_deep(db)

@router.get("/completeness")
def get_extraction_completeness(
    statement_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Returns field completeness metrics across extracted transaction records."""
    return AnalyticsService.get_extraction_completeness(db, statement_id=statement_id)

@router.get("/multi-statement")
def get_multi_statement_comparison(db: Session = Depends(get_db)):
    """Returns cross-statement financial metrics strictly partitioned by currency."""
    return AnalyticsService.get_multi_statement_comparison(db)

@router.get("/category-trends")
def get_category_trends(
    statement_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Returns timeline of category spending for trend charts."""
    return AnalyticsService.get_category_trends(db, statement_id=statement_id)


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database.session import get_db
from app.services.reconciliation_service import ReconciliationService

router = APIRouter(prefix="/reconciliation", tags=["Reconciliation"])

@router.get("/{statement_id}")
def get_statement_reconciliation(statement_id: str, db: Session = Depends(get_db)):
    """Fetches reconciliation analysis, balance variance, and exceptions for a statement."""
    try:
        return ReconciliationService.reconcile_statement(db, statement_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{statement_id}/run")
def run_statement_reconciliation(statement_id: str, db: Session = Depends(get_db)):
    """Executes a fresh reconciliation run and running-balance verification on a statement."""
    try:
        return ReconciliationService.reconcile_statement(db, statement_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


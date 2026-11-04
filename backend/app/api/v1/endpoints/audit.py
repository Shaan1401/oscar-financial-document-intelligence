from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional

from app.database.session import get_db
from app.database.models import AuditEvent

router = APIRouter(prefix="/audit", tags=["Audit Trail"])

@router.get("")
def list_audit_events(
    event_type: Optional[str] = Query(None),
    statement_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Returns chronological audit trail records of operations, corrections, and uploads."""
    query = db.query(AuditEvent)

    if event_type:
        query = query.filter(AuditEvent.event_type == event_type.upper())
    if statement_id:
        query = query.filter(AuditEvent.statement_id == statement_id)

    total = query.count()
    items = query.order_by(AuditEvent.id.desc()).offset(offset).limit(limit).all()

    return {
        "total": total,
        "items": [
            {
                "id": a.id,
                "actor": a.actor,
                "event_type": a.event_type,
                "statement_id": a.statement_id,
                "transaction_id": a.transaction_id,
                "details": a.details,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in items
        ],
    }


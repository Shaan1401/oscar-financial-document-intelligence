from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import Statement, Transaction, Account, AuditEvent
from app.exports.excel_exporter import ExcelExporter
from app.exports.csv_exporter import CSVExporter

router = APIRouter(prefix="/exports", tags=["Exports"])

@router.get("/{statement_id}/excel")
def export_to_excel(statement_id: str, db: Session = Depends(get_db)):
    stmt = db.query(Statement).filter(Statement.id == statement_id).first()
    if not stmt:
        raise HTTPException(status_code=404, detail="Statement not found")

    txns = db.query(Transaction).filter(Transaction.statement_id == statement_id).order_by(Transaction.id.asc()).all()
    account = db.query(Account).filter(Account.statement_id == statement_id).first()

    excel_bytes = ExcelExporter.export_statement(stmt, txns, account)

    # Log Audit Event
    audit = AuditEvent(
        actor="USER",
        event_type="EXPORT",
        statement_id=statement_id,
        details=f"Exported Excel workbook for '{stmt.filename}' ({len(txns)} records)",
    )
    db.add(audit)
    db.commit()

    clean_filename = f"OSCAR_{stmt.filename.replace('.pdf', '')}_Export.xlsx"
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{clean_filename}"'},
    )

@router.get("/{statement_id}/csv")
def export_to_csv(statement_id: str, db: Session = Depends(get_db)):
    stmt = db.query(Statement).filter(Statement.id == statement_id).first()
    if not stmt:
        raise HTTPException(status_code=404, detail="Statement not found")

    txns = db.query(Transaction).filter(Transaction.statement_id == statement_id).order_by(Transaction.id.asc()).all()
    csv_text = CSVExporter.export_transactions(txns)

    # Log Audit Event
    audit = AuditEvent(
        actor="USER",
        event_type="EXPORT",
        statement_id=statement_id,
        details=f"Exported CSV for '{stmt.filename}' ({len(txns)} records)",
    )
    db.add(audit)
    db.commit()

    clean_filename = f"OSCAR_{stmt.filename.replace('.pdf', '')}_Export.csv"
    # Prepend UTF-8 BOM so Excel opens non-ASCII and symbols accurately
    bom_csv = "\ufeff" + csv_text
    return Response(
        content=bom_csv.encode("utf-8"),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{clean_filename}"'},
    )

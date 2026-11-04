import os
import io
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Response, Query
from sqlalchemy.orm import Session
import pymupdf

from app.database.session import get_db
from app.database.models import Statement, Account, Transaction, AuditEvent
from app.schemas.statement import StatementResponse, StatementUploadResponse, AccountInfoSchema
from app.services.statement_processor import StatementProcessor
from app.validation.normalizer import FinancialNormalizer

router = APIRouter(prefix="/statements", tags=["Statements"])

def serialize_statement(stmt: Statement, db: Session) -> StatementResponse:
    txns = db.query(Transaction).filter(Transaction.statement_id == stmt.id).all()
    accounts = db.query(Account).filter(Account.statement_id == stmt.id).all()

    op_bal = float(FinancialNormalizer.to_decimal(stmt.opening_balance_minor, stmt.exponent)) if stmt.opening_balance_minor is not None else None
    cl_bal = float(FinancialNormalizer.to_decimal(stmt.closing_balance_minor, stmt.exponent)) if stmt.closing_balance_minor is not None else None
    tot_dr = float(FinancialNormalizer.to_decimal(stmt.total_debits_minor, stmt.exponent))
    tot_cr = float(FinancialNormalizer.to_decimal(stmt.total_credits_minor, stmt.exponent))
    exp_cl = float(FinancialNormalizer.to_decimal(stmt.expected_closing_minor, stmt.exponent)) if stmt.expected_closing_minor is not None else None
    var_minor = float(FinancialNormalizer.to_decimal(stmt.variance_minor, stmt.exponent)) if stmt.variance_minor is not None else None

    return StatementResponse(
        id=stmt.id,
        filename=stmt.filename,
        file_hash=stmt.file_hash,
        bank_name=stmt.bank_name,
        layout_type=stmt.layout_type,
        pdf_type=stmt.pdf_type,
        page_count=stmt.page_count,
        statement_period=stmt.statement_period,
        start_date=stmt.start_date,
        end_date=stmt.end_date,
        opening_balance=op_bal,
        closing_balance=cl_bal,
        total_debits=tot_dr,
        total_credits=tot_cr,
        expected_closing=exp_cl,
        variance=var_minor,
        reconciliation_status=stmt.reconciliation_status,
        status=stmt.status,
        error_message=stmt.error_message,
        transaction_count=len(txns),
        created_at=stmt.created_at,
        accounts=[AccountInfoSchema.model_validate(a) for a in accounts],
    )

@router.post("/upload", response_model=StatementResponse)
async def upload_statement(
    file: UploadFile = File(...),
    auto_process: bool = Query(True, description="Automatically process and extract after upload"),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    content = await file.read()
    try:
        stmt = StatementProcessor.save_and_validate_upload(db, content, file.filename)
        if auto_process:
            stmt = StatementProcessor.process_statement(db, stmt.id)
        return serialize_statement(stmt, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=List[StatementResponse])
def list_statements(db: Session = Depends(get_db)):
    stmts = db.query(Statement).order_by(Statement.created_at.desc()).all()
    return [serialize_statement(s, db) for s in stmts]

@router.get("/{statement_id}", response_model=StatementResponse)
def get_statement(statement_id: str, db: Session = Depends(get_db)):
    stmt = db.query(Statement).filter(Statement.id == statement_id).first()
    if not stmt:
        raise HTTPException(status_code=404, detail="Statement not found")
    return serialize_statement(stmt, db)

@router.get("/{statement_id}/status")
def get_statement_status(statement_id: str, db: Session = Depends(get_db)):
    stmt = db.query(Statement).filter(Statement.id == statement_id).first()
    if not stmt:
        raise HTTPException(status_code=404, detail="Statement not found")
    return {
        "id": stmt.id,
        "status": stmt.status,
        "pdf_type": stmt.pdf_type,
        "error_message": stmt.error_message,
    }

@router.post("/{statement_id}/process", response_model=StatementResponse)
def reprocess_statement(statement_id: str, db: Session = Depends(get_db)):
    stmt = StatementProcessor.process_statement(db, statement_id)
    return serialize_statement(stmt, db)

@router.delete("/{statement_id}")
def delete_statement(statement_id: str, db: Session = Depends(get_db)):
    stmt = db.query(Statement).filter(Statement.id == statement_id).first()
    if not stmt:
        raise HTTPException(status_code=404, detail="Statement not found")

    # Delete physical file
    if os.path.exists(stmt.file_path):
        try:
            os.remove(stmt.file_path)
        except OSError:
            pass

    # Log audit event before deletion
    audit = AuditEvent(
        actor="USER",
        event_type="DELETION",
        statement_id=statement_id,
        details=f"Deleted statement '{stmt.filename}' and all associated records",
    )
    db.add(audit)
    db.delete(stmt)
    db.commit()
    return {"message": f"Statement {statement_id} deleted successfully"}

@router.get("/{statement_id}/pages/{page_number}/preview")
def get_page_preview(statement_id: str, page_number: int, db: Session = Depends(get_db)):
    """Renders a PDF page to PNG for the interactive split-screen Evidence Viewer."""
    stmt = db.query(Statement).filter(Statement.id == statement_id).first()
    if not stmt or not os.path.exists(stmt.file_path):
        raise HTTPException(status_code=404, detail="Statement or file not found")

    try:
        doc = pymupdf.open(stmt.file_path)
        if page_number < 1 or page_number > len(doc):
            doc.close()
            raise HTTPException(status_code=400, detail="Page number out of range")
        
        page = doc[page_number - 1]
        pix = page.get_pixmap(dpi=150)
        png_bytes = pix.tobytes("png")
        doc.close()

        return Response(content=png_bytes, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to render page preview: {str(e)}")

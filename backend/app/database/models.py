import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, Index
)
from sqlalchemy.orm import relationship
from app.database.session import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Statement(Base):
    __tablename__ = "statements"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    filename = Column(String(255), nullable=False)
    file_hash = Column(String(64), nullable=False, index=True)
    file_path = Column(String(512), nullable=False)
    bank_name = Column(String(100), nullable=True)
    layout_type = Column(String(50), default="generic")
    pdf_type = Column(String(30), default="text")  # text, scanned, mixed
    page_count = Column(Integer, default=1)
    statement_period = Column(String(100), nullable=True)
    start_date = Column(String(20), nullable=True)
    end_date = Column(String(20), nullable=True)
    
    # Financial summary stored in integer minor units
    opening_balance_minor = Column(Integer, nullable=True)
    closing_balance_minor = Column(Integer, nullable=True)
    total_debits_minor = Column(Integer, default=0)
    total_credits_minor = Column(Integer, default=0)
    expected_closing_minor = Column(Integer, nullable=True)
    variance_minor = Column(Integer, nullable=True)
    currency = Column(String(10), default="INR")
    exponent = Column(Integer, default=2)

    reconciliation_status = Column(String(30), default="PENDING")  # RECONCILED, MISMATCH, INSUFFICIENT_DATA, REVIEW_REQUIRED
    status = Column(String(30), default="UPLOADED")  # UPLOADED, PARSING, PROCESSED, FAILED
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    accounts = relationship("Account", back_populates="statement", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="statement", cascade="all, delete-orphan")
    processing_jobs = relationship("ProcessingJob", back_populates="statement", cascade="all, delete-orphan")


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    statement_id = Column(String(36), ForeignKey("statements.id", ondelete="CASCADE"), nullable=False, index=True)
    holder_name = Column(String(200), nullable=True)
    account_number = Column(String(50), nullable=True)
    masked_number = Column(String(50), nullable=True)
    ifsc_code = Column(String(30), nullable=True)
    branch = Column(String(150), nullable=True)
    currency = Column(String(10), default="INR")

    statement = relationship("Statement", back_populates="accounts")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    statement_id = Column(String(36), ForeignKey("statements.id", ondelete="CASCADE"), nullable=False, index=True)
    
    date = Column(String(20), nullable=False, index=True)
    description = Column(String(500), nullable=False)
    raw_description = Column(Text, nullable=False)
    
    # Monetary values in integer minor units (avoid floating point errors)
    debit_minor = Column(Integer, default=0)
    credit_minor = Column(Integer, default=0)
    balance_minor = Column(Integer, nullable=True)
    currency = Column(String(10), default="INR")
    exponent = Column(Integer, default=2)

    # Classification fields
    category = Column(String(80), default="Other / Unclassified", index=True)
    classification_method = Column(String(30), default="NONE")  # RULE_BASED, MACHINE_LEARNING, MANUAL, NEEDS_REVIEW
    confidence_score = Column(Float, nullable=True)
    classification_reason = Column(String(255), nullable=True)
    rule_id = Column(String(50), nullable=True)
    model_version = Column(String(30), nullable=True)

    # Review & validation
    review_status = Column(String(30), default="APPROVED")  # APPROVED, NEEDS_REVIEW, CORRECTED
    validation_status = Column(String(30), default="VALID")  # VALID, WARNING, ANOMALY
    validation_warnings = Column(String(255), nullable=True)
    
    # Audit & Traceability
    source_page = Column(Integer, default=1)
    row_sequence = Column(Integer, default=0)
    extraction_method = Column(String(30), default="digital_text")  # digital_text, ocr
    bounding_box = Column(String(100), nullable=True)  # "x0,y0,x1,y1"
    
    # Anomaly flags
    is_duplicate = Column(Boolean, default=False)
    is_anomaly = Column(Boolean, default=False)

    statement = relationship("Statement", back_populates="transactions")
    classification_events = relationship("ClassificationEvent", back_populates="transaction", cascade="all, delete-orphan")
    review_events = relationship("ReviewEvent", back_populates="transaction", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_txn_statement_date", "statement_id", "date"),
        Index("idx_txn_category", "category"),
    )


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80), unique=True, nullable=False)
    category_type = Column(String(30), default="EXPENSE")  # INCOME, EXPENSE, TRANSFER, CHARGES
    description = Column(String(255), nullable=True)
    color_code = Column(String(20), default="#64748B")
    icon_name = Column(String(50), default="tag")


class ClassificationEvent(Base):
    __tablename__ = "classification_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, index=True)
    method = Column(String(30), nullable=False)
    category = Column(String(80), nullable=False)
    rule_id = Column(String(50), nullable=True)
    model_version = Column(String(30), nullable=True)
    confidence_score = Column(Float, nullable=True)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    transaction = relationship("Transaction", back_populates="classification_events")


class ReviewEvent(Base):
    __tablename__ = "review_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, index=True)
    old_category = Column(String(80), nullable=False)
    new_category = Column(String(80), nullable=False)
    action = Column(String(30), nullable=False)  # APPROVE, CORRECT, RECLASSIFY
    reason = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    transaction = relationship("Transaction", back_populates="review_events")


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    statement_id = Column(String(36), ForeignKey("statements.id", ondelete="CASCADE"), nullable=False, index=True)
    stage = Column(String(50), nullable=False)  # UPLOAD, VALIDATE, EXTRACT, PARSE, CLASSIFY, RECONCILE
    status = Column(String(30), nullable=False)  # STARTED, COMPLETED, FAILED
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    statement = relationship("Statement", back_populates="processing_jobs")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    actor = Column(String(50), default="SYSTEM")
    event_type = Column(String(50), nullable=False, index=True)  # UPLOAD, EXTRACTION, CLASSIFICATION, CORRECTION, RECONCILIATION, EXPORT, DELETION
    statement_id = Column(String(36), nullable=True, index=True)
    transaction_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)


class ParserProfile(Base):
    __tablename__ = "parser_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bank_name = Column(String(100), nullable=False)
    layout_name = Column(String(100), nullable=False)
    config_json = Column(Text, nullable=False)
    version = Column(String(20), default="1.0.0")
    is_active = Column(Boolean, default=True)

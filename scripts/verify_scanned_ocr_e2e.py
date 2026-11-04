"""
OSCAR — End-to-End Physical Tesseract OCR Integration Verification
Processes genuine scanned raster bitmap PDFs through OSCAR's live REST API,
verifies OCR execution, evaluates precision/recall/field-level accuracy against
ground truth, verifies SQLite persistence with coordinates, and tests handling
of degraded/poor quality scanned documents.
"""

import os
import sys
import time
import json
import uuid
from pathlib import Path
from decimal import Decimal
import urllib.request
import urllib.parse
from PIL import Image, ImageFilter, ImageEnhance
import pymupdf

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "backend"))

from app.database.session import SessionLocal
from app.database.models import Statement, Transaction, Account, AuditEvent
from app.validation.normalizer import FinancialNormalizer

API_BASE = "http://127.0.0.1:8000/api/v1"


def normalize_date(d: str) -> str:
    d = str(d).strip()
    if "/" in d:
        parts = d.split("/")
        if len(parts[0]) == 4:
            return f"{parts[0]}-{int(parts[1]):02d}-{int(parts[2]):02d}"
        elif len(parts) >= 3 and len(parts[2]) == 4:
            return f"{parts[2]}-{int(parts[1]):02d}-{int(parts[0]):02d}"
    elif "-" in d:
        parts = d.split("-")
        if len(parts[0]) == 4:
            return f"{parts[0]}-{int(parts[1]):02d}-{int(parts[2]):02d}"
        elif len(parts) >= 3 and len(parts[2]) == 4:
            return f"{parts[2]}-{int(parts[1]):02d}-{int(parts[0]):02d}"
    return d

def upload_statement_file(file_path: Path, filename: str) -> dict:
    """Uploads a PDF file using multipart form data to OSCAR API."""
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    body = bytearray()
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode("utf-8"))
    body.extend(b"Content-Type: application/pdf\r\n\r\n")
    body.extend(file_bytes)
    body.extend(f"\r\n--{boundary}--\r\n".encode("utf-8"))

    req = urllib.request.Request(
        f"{API_BASE}/statements/upload?auto_process=true",
        data=bytes(body),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def test_standard_scanned_statement():
    print("=" * 70)
    print("TEST 1: LIVE SCANNED STATEMENT PROCESSING VIA TESSERACT OCR")
    print("=" * 70)

    source_scanned_pdf = REPO_ROOT / "sample_data" / "pdf" / "synthetic_statement_scanned.pdf"
    gt_file = REPO_ROOT / "sample_data" / "ground_truth" / "synthetic_statement_layout_a_truth.json"

    assert source_scanned_pdf.exists(), f"Scanned PDF not found at {source_scanned_pdf}"
    assert gt_file.exists(), f"Ground truth not found at {gt_file}"

    with open(gt_file, "r", encoding="utf-8") as f:
        ground_truth = json.load(f)

    # Salt PDF bytes so upload hash is unique for this test run
    salt = f"\n%ocr_physical_test_{int(time.time())}".encode("utf-8")
    with open(source_scanned_pdf, "rb") as f:
        salted_bytes = f.read() + salt

    temp_pdf = REPO_ROOT / "backend" / "storage" / f"temp_scanned_test_{uuid.uuid4().hex[:8]}.pdf"
    with open(temp_pdf, "wb") as f:
        f.write(salted_bytes)

    try:
        print(f"Uploading scanned PDF ({len(salted_bytes)} bytes) to /api/v1/statements/upload...")
        t0 = time.time()
        upload_resp = upload_statement_file(temp_pdf, f"scanned_statement_{int(time.time())}.pdf")
        elapsed = time.time() - t0
        print(f"Upload and processing completed in {elapsed:.2f}s!")

        stmt_id = upload_resp["id"]
        print(f"Assigned Statement ID: {stmt_id}")
        print(f"Reported PDF Type:     {upload_resp['pdf_type']}")
        print(f"Reconciliation Status: {upload_resp['reconciliation_status']}")
        print(f"Transaction Count:     {upload_resp['transaction_count']}")

        # 1. Fetch full statement detail contract
        detail_url = f"{API_BASE}/statements/{stmt_id}"
        with urllib.request.urlopen(detail_url) as resp:
            detail_data = json.loads(resp.read().decode("utf-8"))

        txns = detail_data["transactions"]
        print(f"\nRetrieved {len(txns)} transactions from API.")

        # 2. Verify OCR Execution (not digital text)
        print("\n--- Verifying OCR Execution Method & Coordinate Bounding Boxes ---")
        ocr_count = sum(1 for t in txns if t.get("extraction_method") == "ocr")
        has_bboxes = sum(1 for t in txns if t.get("bounding_box"))
        print(f"Transactions with extraction_method='ocr': {ocr_count}/{len(txns)}")
        print(f"Transactions with spatial bounding boxes:  {has_bboxes}/{len(txns)}")

        assert upload_resp["pdf_type"] == "scanned", f"Expected pdf_type='scanned', got {upload_resp['pdf_type']}"
        assert ocr_count == len(txns), f"Expected all transactions to have extraction_method='ocr', got {ocr_count}"
        assert has_bboxes == len(txns), f"Expected all transactions to have bounding boxes, got {has_bboxes}"

        # 3. Ground Truth Comparison & Accuracy Calculation
        print("\n--- Comparing Extracted Transactions Against Ground Truth ---")
        gt_txns = ground_truth["transactions"]
        total_gt = len(gt_txns)
        total_extracted = len(txns)

        matched_txns = 0
        date_correct = 0
        debit_correct = 0
        credit_correct = 0
        balance_correct = 0
        desc_matches = 0

        for i, gt in enumerate(gt_txns):
            if i >= len(txns):
                break
            ex = txns[i]

            # Normalize dates (YYYY-MM-DD vs DD/MM/YYYY)
            gt_date = normalize_date(gt["date"])
            ex_date = normalize_date(ex["date"])

            d_match = (gt_date == ex_date)
            dr_match = (Decimal(str(gt["debit"])) == Decimal(str(ex["debit"])))
            cr_match = (Decimal(str(gt["credit"])) == Decimal(str(ex["credit"])))
            bal_match = (Decimal(str(gt["balance"])) == Decimal(str(ex["balance"])))

            # Fuzzy / token similarity for description
            gt_desc_tokens = set(gt["description"].upper().split())
            ex_desc_tokens = set(ex["description"].upper().split())
            overlap = len(gt_desc_tokens.intersection(ex_desc_tokens))
            desc_ok = (overlap >= 2) or (overlap == len(gt_desc_tokens))

            if d_match:
                date_correct += 1
            if dr_match:
                debit_correct += 1
            if cr_match:
                credit_correct += 1
            if bal_match:
                balance_correct += 1
            if desc_ok:
                desc_matches += 1

            if d_match and dr_match and cr_match and bal_match:
                matched_txns += 1

            print(f"Row {i+1:02d}: GT [{gt['date']} | {gt['description'][:22]} | Dr:{gt['debit']:>7.2f} | Cr:{gt['credit']:>8.2f} | Bal:{gt['balance']:>9.2f}]")
            print(f"   OCR: [{ex['date']} | {ex['description'][:22]} | Dr:{ex['debit']:>7.2f} | Cr:{ex['credit']:>8.2f} | Bal:{ex['balance']:>9.2f}]")
            status_flag = "EXACT MATCH" if (d_match and dr_match and cr_match and bal_match) else "PARTIAL MATCH"
            print(f"        -> {status_flag} (BBox: {ex.get('bounding_box')[:30]}...)")

        precision = matched_txns / total_extracted if total_extracted > 0 else 0.0
        recall = matched_txns / total_gt if total_gt > 0 else 0.0
        date_acc = date_correct / total_gt
        debit_acc = debit_correct / total_gt
        credit_acc = credit_correct / total_gt
        balance_acc = balance_correct / total_gt
        desc_acc = desc_matches / total_gt
        overall_field_acc = (date_acc + debit_acc + credit_acc + balance_acc + desc_acc) / 5.0

        print("\n" + "=" * 50)
        print("TESSERACT OCR EXTRACTION BENCHMARK RESULTS")
        print("=" * 50)
        print(f"Ground Truth Transactions: {total_gt}")
        print(f"Extracted Transactions:    {total_extracted}")
        print(f"Precision:                 {precision * 100:.2f}% ({matched_txns}/{total_extracted})")
        print(f"Recall:                    {recall * 100:.2f}% ({matched_txns}/{total_gt})")
        print(f"Date Field Accuracy:       {date_acc * 100:.2f}% ({date_correct}/{total_gt})")
        print(f"Debit Field Accuracy:      {debit_acc * 100:.2f}% ({debit_correct}/{total_gt})")
        print(f"Credit Field Accuracy:     {credit_acc * 100:.2f}% ({credit_correct}/{total_gt})")
        print(f"Balance Field Accuracy:    {balance_acc * 100:.2f}% ({balance_correct}/{total_gt})")
        print(f"Description Match Rate:    {desc_acc * 100:.2f}% ({desc_matches}/{total_gt})")
        print(f"Overall Field Accuracy:    {overall_field_acc * 100:.2f}%")
        print("=" * 50)

        # 4. Verify SQLite Database Records Directly
        print("\n--- Verifying SQLite Persistence Directly ---")
        db = SessionLocal()
        try:
            db_stmt = db.query(Statement).filter(Statement.id == stmt_id).first()
            assert db_stmt is not None, "Statement must exist in SQLite oscar.db"
            assert db_stmt.pdf_type == "scanned"
            assert db_stmt.reconciliation_status == "RECONCILED"
            assert db_stmt.variance_minor == 0

            db_txns = db.query(Transaction).filter(Transaction.statement_id == stmt_id).all()
            assert len(db_txns) == total_extracted
            for dt in db_txns:
                assert dt.extraction_method == "ocr"
                assert dt.bounding_box is not None
            print(f"Direct SQLite Query: Statement {stmt_id} contains {len(db_txns)} persisted OCR transactions.")
        finally:
            db.close()

        # 5. Clean up test statement from oscar.db to keep database pristine
        db_clean = SessionLocal()
        try:
            s_del = db_clean.query(Statement).filter(Statement.id == stmt_id).first()
            if s_del:
                db_clean.delete(s_del)
                db_clean.commit()
                print(f"Test statement {stmt_id} cleanly removed from oscar.db.")
        finally:
            db_clean.close()

        return {
            "total_gt": total_gt,
            "total_extracted": total_extracted,
            "precision": precision,
            "recall": recall,
            "date_acc": date_acc,
            "debit_acc": debit_acc,
            "credit_acc": credit_acc,
            "balance_acc": balance_acc,
            "overall_field_acc": overall_field_acc,
            "elapsed_seconds": elapsed,
        }

    finally:
        if temp_pdf.exists():
            temp_pdf.unlink()


def test_poor_quality_degraded_scanned_statement():
    print("\n" + "=" * 70)
    print("TEST 2: DEGRADED / POOR QUALITY SCANNED STATEMENT & UNCERTAINTY HANDLING")
    print("=" * 70)

    source_scanned_pdf = REPO_ROOT / "sample_data" / "pdf" / "synthetic_statement_scanned.pdf"
    doc = pymupdf.open(str(source_scanned_pdf))
    pix = doc[0].get_pixmap(dpi=100)  # Degrade resolution to 100 DPI
    pil_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    # Apply degradation: heavy blur, low contrast, brightness wash
    degraded = pil_img.filter(ImageFilter.GaussianBlur(radius=1.8))
    contrast_enhancer = ImageEnhance.Contrast(degraded)
    degraded = contrast_enhancer.enhance(0.4)  # Low contrast 40%
    brightness_enhancer = ImageEnhance.Brightness(degraded)
    degraded = brightness_enhancer.enhance(1.3)  # Over-exposed wash

    # Save to a degraded PDF
    degraded_pdf_path = REPO_ROOT / "backend" / "storage" / f"temp_degraded_{uuid.uuid4().hex[:8]}.pdf"
    degraded.save(degraded_pdf_path, "PDF", resolution=100.0)
    doc.close()

    try:
        print(f"Uploading degraded statement ({degraded_pdf_path.stat().st_size} bytes)...")
        upload_resp = upload_statement_file(degraded_pdf_path, f"degraded_scan_{int(time.time())}.pdf")
        deg_id = upload_resp["id"]

        print(f"Degraded Statement ID:     {deg_id}")
        print(f"Degraded PDF Type:         {upload_resp['pdf_type']}")
        print(f"Degraded Recon Status:     {upload_resp['reconciliation_status']}")
        print(f"Degraded Extracted Count:  {upload_resp['transaction_count']}")

        detail_url = f"{API_BASE}/statements/{deg_id}"
        with urllib.request.urlopen(detail_url) as resp:
            deg_detail = json.loads(resp.read().decode("utf-8"))

        deg_txns = deg_detail.get("transactions", [])
        print(f"Extracted transactions from heavily degraded scan: {len(deg_txns)}")

        # Uncertainty handling evaluation:
        # Check review status or reconciliation status when images are blurred/unreadable
        print("\n--- Evaluating Uncertainty Handling on Degraded Input ---")
        if upload_resp["reconciliation_status"] in ("MISMATCH", "INSUFFICIENT_DATA", "REVIEW_REQUIRED"):
            print(f"[UNCERTAINTY HANDLED] Statement reconciliation flagged as: {upload_resp['reconciliation_status']}")
        else:
            print(f"Reconciliation status: {upload_resp['reconciliation_status']}")

        flagged_count = sum(1 for t in deg_txns if t.get("review_status") in ("NEEDS_REVIEW", "FLAGGED") or (t.get("confidence_score") or 1.0) < 0.65)
        print(f"Transactions routed to human review or flagged: {flagged_count}/{len(deg_txns)}")

        # Clean up degraded test statement
        db_clean = SessionLocal()
        try:
            s_del = db_clean.query(Statement).filter(Statement.id == deg_id).first()
            if s_del:
                db_clean.delete(s_del)
                db_clean.commit()
                print(f"Degraded test statement {deg_id} cleanly removed from oscar.db.")
        finally:
            db_clean.close()

        return {
            "status": upload_resp["status"],
            "recon_status": upload_resp["reconciliation_status"],
            "extracted_count": len(deg_txns),
            "flagged_count": flagged_count,
        }

    finally:
        if degraded_pdf_path.exists():
            degraded_pdf_path.unlink()


if __name__ == "__main__":
    res1 = test_standard_scanned_statement()
    res2 = test_poor_quality_degraded_scanned_statement()
    print("\nALL SCANNED OCR VERIFICATION TESTS COMPLETED SUCCESSFULLY!")

import pytest
from pathlib import Path
from PIL import Image, ImageDraw

from app.core.config import settings
from app.extraction.text_extractor import DocumentExtractor
from app.extraction.ocr_extractor import TesseractDetector, OCRPreprocessor, OCRExtractor
from app.bank_parsers.generic import GenericBankParser
from app.validation.benchmark import ExtractionBenchmark

SAMPLE_DIR = settings.SAMPLE_DATA_DIR

def test_layout_a_benchmark():
    pdf_path = SAMPLE_DIR / "pdf" / "synthetic_statement_layout_a.pdf"
    gt_path = SAMPLE_DIR / "ground_truth" / "synthetic_statement_layout_a_truth.json"

    assert pdf_path.exists(), "Layout A PDF must exist"
    assert gt_path.exists(), "Layout A Ground Truth must exist"

    results = ExtractionBenchmark.evaluate_pdf_against_ground_truth(pdf_path, gt_path)
    metrics = results["metrics"]

    assert metrics["ground_truth_count"] == 15
    assert metrics["extracted_count"] == 15
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["debit_accuracy"] == 1.0
    assert metrics["credit_accuracy"] == 1.0
    assert metrics["balance_accuracy"] == 1.0
    assert results["metadata_evaluation"]["account_number"]["matched"] is True

def test_layout_b_combined_amount_benchmark():
    pdf_path = SAMPLE_DIR / "pdf" / "synthetic_statement_layout_b.pdf"
    gt_path = SAMPLE_DIR / "ground_truth" / "synthetic_statement_layout_b_truth.json"

    assert pdf_path.exists(), "Layout B PDF must exist"
    assert gt_path.exists(), "Layout B Ground Truth must exist"

    results = ExtractionBenchmark.evaluate_pdf_against_ground_truth(pdf_path, gt_path)
    metrics = results["metrics"]

    assert metrics["ground_truth_count"] == 12
    assert metrics["extracted_count"] == 12
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["debit_accuracy"] == 1.0
    assert metrics["credit_accuracy"] == 1.0
    assert metrics["balance_accuracy"] == 1.0
    assert results["metadata_evaluation"]["account_number"]["matched"] is True

def test_layout_c_multipage_wrapped_benchmark():
    pdf_path = SAMPLE_DIR / "pdf" / "synthetic_statement_layout_c.pdf"
    gt_path = SAMPLE_DIR / "ground_truth" / "synthetic_statement_layout_c_truth.json"

    assert pdf_path.exists(), "Layout C PDF must exist"
    assert gt_path.exists(), "Layout C Ground Truth must exist"

    results = ExtractionBenchmark.evaluate_pdf_against_ground_truth(pdf_path, gt_path)
    metrics = results["metrics"]

    assert metrics["ground_truth_count"] == 20
    assert metrics["extracted_count"] == 20
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["debit_accuracy"] == 1.0
    assert metrics["credit_accuracy"] == 1.0
    assert metrics["balance_accuracy"] == 1.0
    assert results["metadata_evaluation"]["account_number"]["matched"] is True

def test_scanned_pdf_page_type_detection():
    pdf_path = SAMPLE_DIR / "pdf" / "synthetic_statement_scanned.pdf"
    assert pdf_path.exists(), "Scanned PDF must exist"

    doc_data = DocumentExtractor.extract_document(pdf_path)
    assert doc_data["page_count"] >= 1
    assert doc_data["pdf_type"] == "scanned"
    assert doc_data["pages"][0].page_type == "scanned"

def test_tesseract_detector_diagnostics():
    status = TesseractDetector.get_status(refresh=True)
    assert isinstance(status, dict)
    assert "available" in status
    assert "message" in status
    assert "instructions" in status
    if not status["available"]:
        assert "Tesseract OCR" in status["instructions"]

def test_ocr_preprocessor():
    # Create synthetic test bitmap image with text
    img = Image.new("RGB", (400, 100), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((20, 35), "OSCAR OCR TEST 12345", fill="black")

    processed_img, angle = OCRPreprocessor.preprocess(img)
    assert isinstance(processed_img, Image.Image)
    assert processed_img.size == img.size
    assert processed_img.mode in ("L", "1", "RGB")
    assert isinstance(angle, float)

def test_ocr_extractor_handles_unavailable_or_executes():
    img = Image.new("RGB", (300, 80), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((10, 30), "TEST TRANSACTION", fill="black")

    res = OCRExtractor.extract_image_text_and_blocks(img)
    assert "status" in res
    assert res["status"] in ("SUCCESS", "OCR_UNAVAILABLE", "FAILED")
    if res["status"] == "OCR_UNAVAILABLE":
        assert res["text"] == ""
        assert res["error"] is not None

def test_scanned_pdf_tesseract_ocr_extraction():
    status = TesseractDetector.get_status(refresh=True)
    if not status["available"]:
        pytest.skip("Tesseract OCR binary not installed on host")

    pdf_path = SAMPLE_DIR / "pdf" / "synthetic_statement_scanned.pdf"
    assert pdf_path.exists(), "Scanned PDF must exist"

    doc_data = DocumentExtractor.extract_document(pdf_path)
    assert doc_data["pdf_type"] == "scanned"
    assert len(doc_data["pages"]) == 1

    page = doc_data["pages"][0]
    assert page.ocr_status == "SUCCESS"
    assert len(page.tables) >= 1

    parser = GenericBankParser()
    assert parser.can_parse(doc_data) > 0.5
    txns = parser.parse(doc_data)

    assert len(txns) == 15, f"Expected 15 transactions extracted via OCR, got {len(txns)}"
    for t in txns:
        assert t.extraction_method == "ocr"
        assert t.bounding_box is not None
        assert t.date.startswith("2026-")
        assert t.balance is not None


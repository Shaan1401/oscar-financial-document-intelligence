# OSCAR — Next Actions

## Immediate Focus: Phase 2 — Multi-Layout Parsing, OCR Integration & Preprocessing

### Objectives
1. **Three Distinct Synthetic Bank Statement Layouts**:
   - **Layout A**: Standard Separate Debit & Credit columns (already created: `synthetic_statement_layout_a.pdf`).
   - **Layout B**: Single combined amount column with "DR"/"CR" indicators or negative signs (e.g. Axis/ICICI style).
   - **Layout C**: Multi-page statement with wrapped description rows and distinct header naming ("Value Date", "Particulars", "Withdrawals", "Deposits", "Net Balance").
   - **Ground-Truth Data**: JSON files for each layout verifying exact transaction counts, debits, credits, balances.
2. **OCR Engine & Preprocessing**:
   - `ocr_extractor.py`: Preprocessing with OpenCV/Pillow (grayscale, contrast enhancement, adaptive thresholding, deskewing).
   - `TesseractDetector`: Detects tesseract binary in PATH or Windows Program Files; provides graceful fallback and diagnostic error reporting when OCR is unavailable without faking results.
   - Scanned PDF generator producing an image-only PDF to test scanned page detection.
3. **Extraction Benchmark Service**:
   - Compares parsed records against ground truth for row counts, amounts, dates, and account numbers.
4. **Automated Verification**:
   - Pytest suite `backend/tests/test_multi_layout_and_ocr.py`.

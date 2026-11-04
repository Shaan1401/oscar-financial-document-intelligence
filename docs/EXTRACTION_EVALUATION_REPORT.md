# OSCAR PDF Extraction & OCR Ground-Truth Evaluation Report

**Evaluation Benchmark**: PyMuPDF & pdfplumber Native Text Extraction + Tesseract OCR Fallback  
**Ground Truth Corpus**: Indian Banking Synthetic Standard Corpora (Layouts A, B, C & Scanned)  
**Strict Determinism**: Zero Cloud APIs | Exact Bounding Box Coordinate Traceability | Minor-Unit Exactness  
**Generated At**: 2026-11-04 20:51:26 UTC  

---

## 1. Executive Summary

OSCAR parses complex, multi-page Indian banking statements across diverse structural layouts with high extraction fidelity.

| Metric | Portfolio Aggregate | Layout A (Separate Dr/Cr) | Layout B (Combined Type) | Layout C (Multi-Page Wrapped) |
| :--- | :--- | :--- | :--- | :--- |
| **Transaction Precision** | **100.00%** | 100.0% | 100.0% | 100.0% |
| **Transaction Recall** | **100.00%** | 100.0% | 100.0% | 100.0% |
| **Transaction F1-Score** | **100.00%** | 100.0% | 100.0% | 100.0% |
| **Date Parsing Accuracy** | **100.0%** | 100.0% | 100.0% | 100.0% |
| **Debit Amount Accuracy** | **100.0%** | 100.0% | 100.0% | 100.0% |
| **Credit Amount Accuracy** | **100.0%** | 100.0% | 100.0% | 100.0% |
| **Balance Accuracy** | **100.0%** | 100.0% | 100.0% | 100.0% |
| **Extraction Latency** | **250.5 ms** | 304.2 ms | 195.7 ms | 251.5 ms |

---

## 2. Layout Benchmark Details

### Layout A: Multi-Column Separate Debit / Credit
- **Bank Profile**: OSCAR Demonstration Bank (SBI/HDFC Standard Style)
- **Features**: Explicit columns for Date, Narration, Chq/Ref No, Withdrawal (Debit), Deposit (Credit), and Balance.
- **Ground Truth Count**: 15 transactions
- **Extracted Count**: 15 transactions
- **Precision / Recall / F1**: 100.0% / 100.0% / **100.0%**
- **Metadata Verification**:
  - Bank Name: Match
  - Account Number: Match
  - IFSC Code: Match
  - Statement Period: Match

### Layout B: Single Combined Amount with DR/CR Type Indicator
- **Bank Profile**: ICICI / Axis Bank Retail Format
- **Features**: Single `Amount` column with trailing `(Dr)` or `(Cr)` indicator, or separate Type column.
- **Ground Truth Count**: 12 transactions
- **Extracted Count**: 12 transactions
- **Precision / Recall / F1**: 100.0% / 100.0% / **100.0%**
- **Parser Mechanism**: Auto-detects single amount representation and directs positive flow to credit/debit according to type suffix.

### Layout C: Multi-Page Statement with Multi-Line Wrapped Narrations
- **Bank Profile**: Kotak / Federal Corporate Banking Format
- **Features**: Long narrative descriptions spanning 2-3 visual lines per record across multiple pages, with page breaks and running balance headers.
- **Ground Truth Count**: 20 transactions
- **Extracted Count**: 20 transactions
- **Precision / Recall / F1**: 100.0% / 100.0% / **100.0%**
- **Parser Mechanism**: Multi-line row coalescing merges continuation rows by detecting absence of dates on wrapped narration lines.

---

## 3. Optical Character Recognition (OCR) Fallback Evaluation

To process scanned or low-resolution image-based PDFs without digital text layers, OSCAR incorporates an automated OCR triage and extraction pipeline:

| Evaluation Dimension | Metric / Result |
| :--- | :--- |
| **Document Evaluated** | `sample_data/pdf/synthetic_statement_scanned.pdf` |
| **Page Type Classification** | **`scanned`** (Correctly identified zero digital text layer) |
| **OCR Fallback Engine** | Tesseract OCR v5 with image binarization & deskewing |
| **Engine Availability** | `False` |
| **OCR Pipeline Execution** | `OCR_UNAVAILABLE` |
| **Characters Extracted** | `0` characters |
| **Processing Latency** | `127.5 ms` |

---

## 4. Evidence Coordinate Integrity

For every extracted transaction, the engine computes normalized bounding box coordinates:
$$	ext{Bounding Box} = [x_0, y_0, x_1, y_1]$$

These coordinates are persisted in the database and mapped to high-resolution page viewports in the React Evidence Viewer, enabling interactive clicking from transaction tables directly to highlighted PDF segments.

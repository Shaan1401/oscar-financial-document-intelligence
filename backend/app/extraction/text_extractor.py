import re
from pathlib import Path
from decimal import Decimal
from typing import Dict, Any, List, Optional, Tuple
import pymupdf
import pdfplumber
from PIL import Image

from app.validation.normalizer import FinancialNormalizer
from app.extraction.ocr_extractor import OCRExtractor

class PageContent:
    def __init__(
        self,
        page_number: int,
        text: str,
        page_type: str,
        tables: List[List[List[str]]],
        blocks: List[Dict],
        ocr_status: Optional[str] = None,
        ocr_error: Optional[str] = None,
        table_bboxes: Optional[List[List[Optional[str]]]] = None,
        page_width: float = 612.0,
        page_height: float = 792.0,
    ):
        self.page_number = page_number
        self.text = text
        self.page_type = page_type  # text, scanned, mixed
        self.tables = tables
        self.blocks = blocks
        self.ocr_status = ocr_status
        self.ocr_error = ocr_error
        self.table_bboxes = table_bboxes or []
        self.page_width = page_width
        self.page_height = page_height

class DocumentExtractor:
    """Extracts raw text, table structures, and metadata from PDF files using PyMuPDF & pdfplumber."""

    IFSC_REGEX = re.compile(r"\b[A-Z]{4}0[A-Z0-9]{6}\b", re.IGNORECASE)
    ACCOUNT_REGEX = re.compile(
        r"(?:Account|A/c|Acct)(?:\s*(?:No|Number|#))?\s*[:\-\.]?\s*(\d{9,18})\b",
        re.IGNORECASE,
    )
    HOLDER_REGEX = re.compile(
        r"(?:Account\s*Holder(?:\s*Name)?|Customer\s*Name|Name\s*(?:of\s*Account)?)\s*[:\-\.]?\s*([A-Z][A-Za-z\s\.]{2,40}?)(?:\s+(?:Account|Customer|A/c|Acct|IFSC|CIF|ID|Branch)\b|\n|$)",
        re.IGNORECASE,
    )
    BRANCH_REGEX = re.compile(
        r"(?:Branch(?:\s*Name)?)\s*[:\-\.]?\s*([A-Za-z0-9\s,]{3,40}?)(?:\s+(?:Currency|Statement|IFSC|Account)\b|\n|$)",
        re.IGNORECASE,
    )
    PERIOD_REGEX = re.compile(
        r"(?:Statement\s*Period|Period|Date\s*Range)\s*[:\-\.]?\s*([\d\w\s\-/.]+\s*(?:to|-)\s*[\d\w\s\-/.]+?)(?:\s+(?:Opening|Closing|Balance)\b|\n|$)",
        re.IGNORECASE,
    )
    BANK_NAMES = [
        "State Bank of India", "SBI", "HDFC Bank", "HDFC", "ICICI Bank", "ICICI",
        "Axis Bank", "Kotak Mahindra Bank", "Kotak", "Punjab National Bank", "PNB",
        "Bank of Baroda", "BOB", "Canara Bank", "Union Bank of India", "IndusInd Bank",
        "Federal Bank", "Standard Chartered", "Citibank", "OSCAR Demonstration Bank"
    ]

    @classmethod
    def extract_document(cls, pdf_path: str | Path) -> Dict[str, Any]:
        """
        Inspects PDF file page-by-page, extracts text, identifies tables,
        and extracts available account details.
        """
        pdf_path = Path(pdf_path)
        doc = pymupdf.open(str(pdf_path))
        page_count = len(doc)

        pages: List[PageContent] = []
        overall_pdf_type = "text"
        scanned_pages_count = 0

        # Open with pdfplumber for table extraction
        plumber_doc = pdfplumber.open(str(pdf_path))

        full_text_corpus = []

        for p_idx in range(page_count):
            mupdf_page = doc[p_idx]
            raw_text = mupdf_page.get_text()
            full_text_corpus.append(raw_text)
            
            # Detect page type based on text content and image count
            char_count = len(raw_text.strip())
            images = mupdf_page.get_images()
            
            if char_count < 60 and len(images) > 0:
                page_type = "scanned"
                scanned_pages_count += 1
            elif char_count >= 60 and len(images) > 0:
                page_type = "mixed"
            else:
                page_type = "text"

            ocr_status = None
            ocr_error = None
            ocr_res = None

            # For scanned pages, attempt OCR extraction
            if page_type == "scanned":
                try:
                    pix = mupdf_page.get_pixmap(dpi=200)
                    pil_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    ocr_res = OCRExtractor.extract_image_text_and_blocks(pil_img)
                    ocr_status = ocr_res.get("status")
                    ocr_error = ocr_res.get("error")
                    if ocr_status == "SUCCESS" and ocr_res.get("text"):
                        raw_text = ocr_res["text"]
                        full_text_corpus[-1] = raw_text
                except Exception as ex:
                    ocr_status = "FAILED"
                    ocr_error = str(ex)

            # Extract blocks with coordinates for traceability
            blocks = []
            for b in mupdf_page.get_text("blocks"):
                # b is (x0, y0, x1, y1, text, block_no, block_type)
                if len(b) >= 5 and b[4].strip():
                    blocks.append({
                        "bbox": f"{b[0]:.1f},{b[1]:.1f},{b[2]:.1f},{b[3]:.1f}",
                        "text": b[4].strip(),
                    })

            # If no native blocks found (scanned PDF), scale OCR word blocks to PDF coordinates
            scale = 72.0 / 200.0
            if not blocks and ocr_res and ocr_res.get("blocks"):
                for ob in ocr_res["blocks"]:
                    try:
                        parts = [float(x) for x in ob["bbox"].split(",")]
                        if len(parts) == 4:
                            scaled_box = f"{parts[0]*scale:.1f},{parts[1]*scale:.1f},{parts[2]*scale:.1f},{parts[3]*scale:.1f}"
                            blocks.append({"bbox": scaled_box, "text": ob["text"]})
                    except Exception:
                        pass

            # Extract tables using pdfplumber
            tables = []
            table_bboxes = []
            page_w = 612.0
            page_h = 792.0
            if p_idx < len(plumber_doc.pages):
                plumber_page = plumber_doc.pages[p_idx]
                page_w = float(plumber_page.width)
                page_h = float(plumber_page.height)
                found_tables = plumber_page.find_tables()
                if found_tables:
                    for t in found_tables:
                        ext = t.extract()
                        cleaned_table = []
                        row_bboxes = []
                        for r_idx, row in enumerate(ext):
                            cleaned_row = [FinancialNormalizer.clean_text(cell) if cell else "" for cell in row]
                            # Only keep non-empty rows
                            if any(cleaned_row):
                                cleaned_table.append(cleaned_row)
                                if r_idx < len(t.rows):
                                    b = t.rows[r_idx].bbox
                                    row_bboxes.append(f"{b[0]:.1f},{b[1]:.1f},{b[2]:.1f},{b[3]:.1f},{page_w:.1f},{page_h:.1f}")
                                else:
                                    row_bboxes.append(None)
                        if cleaned_table:
                            tables.append(cleaned_table)
                            table_bboxes.append(row_bboxes)
                else:
                    extracted_tables = plumber_page.extract_tables()
                    if extracted_tables:
                        for t in extracted_tables:
                            cleaned_table = []
                            for row in t:
                                cleaned_row = [FinancialNormalizer.clean_text(cell) if cell else "" for cell in row]
                                # Only keep non-empty rows
                                if any(cleaned_row):
                                    cleaned_table.append(cleaned_row)
                            if cleaned_table:
                                tables.append(cleaned_table)
                                table_bboxes.append([None] * len(cleaned_table))

            # If no vector tables found and page was OCR'd, reconstruct tabular structure from OCR text lines
            if not tables and page_type == "scanned" and ocr_status == "SUCCESS" and raw_text:
                ocr_table, ocr_row_bboxes = cls._reconstruct_table_from_ocr(
                    raw_text, ocr_res.get("blocks", []), page_w, page_h
                )
                if len(ocr_table) > 1:
                    tables.append(ocr_table)
                    table_bboxes.append(ocr_row_bboxes)

            pages.append(PageContent(
                page_number=p_idx + 1,
                text=raw_text,
                page_type=page_type,
                tables=tables,
                blocks=blocks,
                ocr_status=ocr_status,
                ocr_error=ocr_error,
                table_bboxes=table_bboxes,
                page_width=page_w,
                page_height=page_h,
            ))

        doc.close()
        plumber_doc.close()

        # Determine overall document type
        if scanned_pages_count == page_count:
            overall_pdf_type = "scanned"
        elif scanned_pages_count > 0:
            overall_pdf_type = "mixed"
        else:
            overall_pdf_type = "text"

        # Extract account information from combined header text (usually page 1)
        header_text = full_text_corpus[0] if full_text_corpus else ""
        account_info = cls._extract_account_info(header_text)

        return {
            "page_count": page_count,
            "pdf_type": overall_pdf_type,
            "pages": pages,
            "account_info": account_info,
        }

    @classmethod
    def _extract_account_info(cls, text: str) -> Dict[str, Optional[str]]:
        """Extracts available account metadata using context-aware regex patterns."""
        info = {
            "bank_name": None,
            "holder_name": None,
            "account_number": None,
            "masked_number": None,
            "ifsc_code": None,
            "branch": None,
            "statement_period": None,
        }

        # Restrict bank name search to top header region (first 15 lines) to avoid matching merchant ATM narrations
        header_lines = "\n".join(text.splitlines()[:15])

        # 1. Bank name detection (sort by length descending to match specific bank names first)
        sorted_banks = sorted(cls.BANK_NAMES, key=len, reverse=True)
        for bank in sorted_banks:
            if re.search(rf"\b{re.escape(bank)}\b", header_lines, re.IGNORECASE):
                info["bank_name"] = bank
                break

        # If not found in top lines, check if any line explicitly mentions "Bank"
        if not info["bank_name"]:
            for bank in sorted_banks:
                if re.search(rf"\b{re.escape(bank)}\b", text[:500], re.IGNORECASE):
                    info["bank_name"] = bank
                    break

        # 2. Account number
        acc_match = cls.ACCOUNT_REGEX.search(text)
        if acc_match:
            acc_num = acc_match.group(1).strip()
            info["account_number"] = acc_num
            info["masked_number"] = FinancialNormalizer.mask_account_number(acc_num)

        # 3. IFSC code
        ifsc_match = cls.IFSC_REGEX.search(text)
        if ifsc_match:
            info["ifsc_code"] = ifsc_match.group(0).upper()

        # 4. Account holder name
        holder_match = cls.HOLDER_REGEX.search(text)
        if holder_match:
            raw_holder = holder_match.group(1).strip()
            # Avoid picking up labels
            if len(raw_holder) > 3 and not any(kw in raw_holder.upper() for kw in ["ACCOUNT", "STATEMENT", "BRANCH", "PERIOD"]):
                info["holder_name"] = raw_holder

        # 5. Branch
        branch_match = cls.BRANCH_REGEX.search(text)
        if branch_match:
            info["branch"] = branch_match.group(1).strip()

        # 6. Statement period
        period_match = cls.PERIOD_REGEX.search(text)
        if period_match:
            info["statement_period"] = period_match.group(1).strip()

        return info

    @classmethod
    def _reconstruct_table_from_ocr(
        cls,
        text: str,
        ocr_blocks: List[Dict[str, Any]],
        page_w: float,
        page_h: float,
    ) -> Tuple[List[List[str]], List[Optional[str]]]:
        """
        Reconstructs tabular transaction rows and coordinate bounding boxes
        from OCR text lines and character/word bounding boxes.
        """
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        date_pattern = re.compile(r"^\s*([0-3]?\d[\/\-\.][0-1]?\d[\/\-\.]\d{2,4})\b")
        num_pattern = re.compile(r"(?:\b|\s)([\d,]+\.\d{2})\b")

        # Extract opening balance to guide directional debit/credit attribution
        op_bal = None
        for l in lines:
            m_op = re.search(r"Opening\s*Balance\s*[:\-\.]?\s*.*?([\d,]+\.\d{2})", l, re.IGNORECASE)
            if m_op:
                try:
                    op_bal = Decimal(m_op.group(1).replace(",", ""))
                    break
                except Exception:
                    pass

        running_bal = op_bal
        table: List[List[str]] = [
            ["Date", "Narration / Description", "Debit", "Credit", "Balance"]
        ]
        table_bboxes: List[Optional[str]] = [None]  # Header has no single transaction bbox

        scale = 72.0 / 200.0  # Convert 200 DPI OCR pixel coordinates to standard PDF points

        for line in lines:
            dm = date_pattern.match(line)
            if not dm:
                continue
            dt_str = dm.group(1)
            rest = line[dm.end():].strip()

            amts = num_pattern.findall(rest)
            if not amts:
                continue

            first_amt_pos = rest.find(amts[0])
            desc = rest[:first_amt_pos].strip()
            desc = re.sub(r"^[=\-~:\s\uFFFD]+", "", desc).strip()
            desc = re.sub(r"[\-~:\s\uFFFD]+$", "", desc).strip()

            debit_str = ""
            credit_str = ""
            bal_str = ""

            if len(amts) >= 2:
                val1 = Decimal(amts[0].replace(",", ""))
                bal_val = Decimal(amts[-1].replace(",", ""))
                bal_str = f"{bal_val:.2f}"

                if running_bal is not None:
                    diff = bal_val - running_bal
                    if diff > 0 and abs(diff - val1) < Decimal("1.00"):
                        credit_str = f"{val1:.2f}"
                    elif diff < 0 and abs(abs(diff) - val1) < Decimal("1.00"):
                        debit_str = f"{val1:.2f}"
                    else:
                        if re.search(r"-\s*" + re.escape(amts[0]), rest):
                            credit_str = f"{val1:.2f}"
                        else:
                            debit_str = f"{val1:.2f}"
                else:
                    if re.search(r"-\s*" + re.escape(amts[0]), rest):
                        credit_str = f"{val1:.2f}"
                    else:
                        debit_str = f"{val1:.2f}"
                running_bal = bal_val
            elif len(amts) == 1:
                val1 = Decimal(amts[0].replace(",", ""))
                upper = (desc + " " + rest).upper()
                if "CR" in upper or "SALARY" in upper or "REFUND" in upper:
                    credit_str = f"{val1:.2f}"
                    if running_bal is not None:
                        running_bal += val1
                else:
                    debit_str = f"{val1:.2f}"
                    if running_bal is not None:
                        running_bal -= val1
                if running_bal is not None:
                    bal_str = f"{running_bal:.2f}"

            table.append([dt_str, desc, debit_str, credit_str, bal_str])

            # Locate bounding box by matching words within this transaction line
            matched_coords = []
            y_ref = None
            for ob in ocr_blocks:
                if dt_str in ob.get("text", ""):
                    try:
                        y_cand = float(ob["bbox"].split(",")[1])
                        if y_cand > 500:  # Transaction rows appear below the statement header
                            y_ref = y_cand
                            break
                    except Exception:
                        pass

            if y_ref is not None:
                for ob in ocr_blocks:
                    try:
                        b_parts = [float(x) for x in ob["bbox"].split(",")]
                        if len(b_parts) == 4 and abs(b_parts[1] - y_ref) < 25:
                            matched_coords.append(b_parts)
                    except Exception:
                        pass
            else:
                for ob in ocr_blocks:
                    w_text = ob.get("text", "")
                    if w_text and (w_text in desc or w_text in amts) and not any(k in w_text for k in ["OSCAR", "Account", "Statement", "Branch", "Balance", "Total"]):
                        try:
                            b_parts = [float(x) for x in ob["bbox"].split(",")]
                            if len(b_parts) == 4:
                                matched_coords.append(b_parts)
                        except Exception:
                            pass

            if matched_coords:
                min_x = min(c[0] for c in matched_coords) * scale
                min_y = min(c[1] for c in matched_coords) * scale
                max_x = max(c[2] for c in matched_coords) * scale
                max_y = max(c[3] for c in matched_coords) * scale
                row_bbox = f"{min_x:.1f},{min_y:.1f},{max_x:.1f},{max_y:.1f},{page_w:.1f},{page_h:.1f}"
            else:
                row_bbox = None
            table_bboxes.append(row_bbox)

        return table, table_bboxes

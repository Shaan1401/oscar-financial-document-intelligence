import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import pymupdf
import pdfplumber

from app.validation.normalizer import FinancialNormalizer

class PageContent:
    def __init__(self, page_number: int, text: str, page_type: str, tables: List[List[List[str]]], blocks: List[Dict]):
        self.page_number = page_number
        self.text = text
        self.page_type = page_type  # text, scanned, mixed
        self.tables = tables
        self.blocks = blocks

class DocumentExtractor:
    """Extracts raw text, table structures, and metadata from PDF files using PyMuPDF & pdfplumber."""

    IFSC_REGEX = re.compile(r"\b[A-Z]{4}0[A-Z0-9]{6}\b", re.IGNORECASE)
    ACCOUNT_REGEX = re.compile(
        r"(?:Account|A/c|Acct)(?:\s*(?:No|Number|#))?\s*[:\-\.]?\s*(\d{9,18})\b",
        re.IGNORECASE,
    )
    HOLDER_REGEX = re.compile(
        r"(?:Account\s*Holder(?:\s*Name)?|Customer\s*Name|Name\s*(?:of\s*Account)?)\s*[:\-\.]?\s*([A-Z][A-Za-z\s\.]{2,40})",
        re.IGNORECASE,
    )
    BRANCH_REGEX = re.compile(
        r"(?:Branch(?:\s*Name)?)\s*[:\-\.]?\s*([A-Za-z0-9\s,]{3,40})",
        re.IGNORECASE,
    )
    PERIOD_REGEX = re.compile(
        r"(?:Statement\s*Period|Period|Date\s*Range)\s*[:\-\.]?\s*([\d\w\s\-/.]+\s*(?:to|-)\s*[\d\w\s\-/.]+)",
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

            # Extract blocks with coordinates for traceability
            blocks = []
            for b in mupdf_page.get_text("blocks"):
                # b is (x0, y0, x1, y1, text, block_no, block_type)
                if len(b) >= 5 and b[4].strip():
                    blocks.append({
                        "bbox": f"{b[0]:.1f},{b[1]:.1f},{b[2]:.1f},{b[3]:.1f}",
                        "text": b[4].strip(),
                    })

            # Extract tables using pdfplumber
            tables = []
            if p_idx < len(plumber_doc.pages):
                plumber_page = plumber_doc.pages[p_idx]
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

            pages.append(PageContent(
                page_number=p_idx + 1,
                text=raw_text,
                page_type=page_type,
                tables=tables,
                blocks=blocks,
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

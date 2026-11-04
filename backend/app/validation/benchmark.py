import json
from pathlib import Path
from decimal import Decimal
from typing import Dict, Any, List, Optional

from app.extraction.text_extractor import DocumentExtractor
from app.bank_parsers.registry import ParserRegistry
from app.validation.normalizer import FinancialNormalizer

class ExtractionBenchmark:
    """
    Evaluates PDF extraction fidelity against ground-truth JSON files.
    Calculates precision, recall, and exact-match accuracy for:
      - Transaction count
      - Dates
      - Descriptions
      - Debit & Credit amounts
      - Running balances
      - Account metadata (holder name, account number, IFSC)
    """

    @classmethod
    def evaluate_pdf_against_ground_truth(
        cls, pdf_path: str | Path, ground_truth_path: str | Path
    ) -> Dict[str, Any]:
        pdf_path = Path(pdf_path)
        ground_truth_path = Path(ground_truth_path)

        with open(ground_truth_path, "r", encoding="utf-8") as f:
            gt_data = json.load(f)

        gt_meta = gt_data.get("metadata", {})
        gt_txns = gt_data.get("transactions", [])

        # Run extraction
        doc_data = DocumentExtractor.extract_document(pdf_path)
        parser = ParserRegistry.select_parser(doc_data)
        extracted_txns = parser.parse(doc_data)
        extracted_meta = doc_data.get("account_info", {})

        # 1. Metadata evaluation
        meta_results = {}
        for key in ["bank_name", "account_holder", "account_number", "ifsc_code"]:
            expected = gt_meta.get(key)
            actual_key = "holder_name" if key == "account_holder" else ("ifsc_code" if key == "ifsc_code" else key)
            actual = extracted_meta.get(actual_key)
            
            matched = False
            if expected and actual:
                matched = (expected.lower() in actual.lower()) or (actual.lower() in expected.lower())
            elif not expected and not actual:
                matched = True

            meta_results[key] = {
                "expected": expected,
                "actual": actual,
                "matched": matched,
            }

        # 2. Transaction evaluation
        gt_count = len(gt_txns)
        ext_count = len(extracted_txns)

        matched_txns = 0
        date_matches = 0
        desc_matches = 0
        debit_matches = 0
        credit_matches = 0
        balance_matches = 0

        # Match transactions sequentially
        min_len = min(gt_count, ext_count)
        for i in range(min_len):
            gt = gt_txns[i]
            ext = extracted_txns[i]

            # Date (compare ISO normalized forms)
            gt_date_norm, _ = FinancialNormalizer.parse_date(gt["date"])
            d_match = (gt["date"] == ext.date) or (gt_date_norm == ext.date)
            if d_match:
                date_matches += 1

            # Description (token overlap)
            gt_tokens = set(gt["description"].upper().split())
            ext_tokens = set(ext.description.upper().split())
            overlap = len(gt_tokens & ext_tokens) / max(len(gt_tokens), 1)
            desc_match = overlap >= 0.5
            if desc_match:
                desc_matches += 1

            # Amounts
            deb_match = abs(float(gt["debit"]) - float(ext.debit)) < 0.01
            if deb_match:
                debit_matches += 1

            cred_match = abs(float(gt["credit"]) - float(ext.credit)) < 0.01
            if cred_match:
                credit_matches += 1

            bal_match = True
            if ext.balance is not None and gt.get("balance") is not None:
                bal_match = abs(float(gt["balance"]) - float(ext.balance)) < 0.01
            if bal_match:
                balance_matches += 1

            if d_match and deb_match and cred_match and bal_match:
                matched_txns += 1

        precision = matched_txns / ext_count if ext_count > 0 else 0.0
        recall = matched_txns / gt_count if gt_count > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        return {
            "layout_name": gt_meta.get("layout", "Unknown"),
            "pdf_type": doc_data["pdf_type"],
            "parser_used": parser.name,
            "metrics": {
                "ground_truth_count": gt_count,
                "extracted_count": ext_count,
                "fully_matched_transactions": matched_txns,
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1_score": round(f1, 4),
                "date_accuracy": round(date_matches / min_len if min_len > 0 else 0.0, 4),
                "description_token_accuracy": round(desc_matches / min_len if min_len > 0 else 0.0, 4),
                "debit_accuracy": round(debit_matches / min_len if min_len > 0 else 0.0, 4),
                "credit_accuracy": round(credit_matches / min_len if min_len > 0 else 0.0, 4),
                "balance_accuracy": round(balance_matches / min_len if min_len > 0 else 0.0, 4),
            },
            "metadata_evaluation": meta_results,
        }

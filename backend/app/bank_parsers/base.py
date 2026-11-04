from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from decimal import Decimal

class ParsedTransaction:
    def __init__(
        self,
        date: str,
        description: str,
        raw_description: str,
        debit: Decimal,
        credit: Decimal,
        balance: Optional[Decimal],
        source_page: int,
        row_sequence: int,
        bounding_box: Optional[str] = None,
        extraction_method: str = "digital_text",
        validation_warnings: Optional[str] = None,
    ):
        self.date = date
        self.description = description
        self.raw_description = raw_description
        self.debit = debit
        self.credit = credit
        self.balance = balance
        self.source_page = source_page
        self.row_sequence = row_sequence
        self.bounding_box = bounding_box
        self.extraction_method = extraction_method
        self.validation_warnings = validation_warnings

class BaseBankParser(ABC):
    """Abstract base class for all bank statement layout parsers."""

    name: str = "BaseBankParser"
    layout_type: str = "generic"

    @abstractmethod
    def can_parse(self, doc_data: Dict[str, Any]) -> float:
        """
        Evaluates extracted document data and returns confidence score [0.0, 1.0]
        indicating how well this parser matches the layout.
        """
        pass

    @abstractmethod
    def parse(self, doc_data: Dict[str, Any]) -> List[ParsedTransaction]:
        """Parses extracted pages/tables into structured ParsedTransaction objects."""
        pass

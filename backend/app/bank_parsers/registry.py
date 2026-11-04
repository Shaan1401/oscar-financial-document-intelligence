from typing import List, Dict, Any, Type
from app.bank_parsers.base import BaseBankParser
from app.bank_parsers.generic import GenericBankParser
from app.core.errors import ParserNotFoundError

class ParserRegistry:
    """Registry maintaining available bank layout parsers."""

    _parsers: List[BaseBankParser] = []

    @classmethod
    def register(cls, parser: BaseBankParser):
        cls._parsers.append(parser)

    @classmethod
    def get_parsers(cls) -> List[BaseBankParser]:
        if not cls._parsers:
            # Register default parsers
            cls._parsers = [
                GenericBankParser(),
            ]
        return cls._parsers

    @classmethod
    def select_parser(cls, doc_data: Dict[str, Any]) -> BaseBankParser:
        """Evaluates all registered parsers and returns the best matching instance."""
        best_parser = None
        highest_score = -1.0

        for parser in cls.get_parsers():
            score = parser.can_parse(doc_data)
            if score > highest_score:
                highest_score = score
                best_parser = parser

        if best_parser is None or highest_score < 0.10:
            raise ParserNotFoundError("Could not find a matching bank parser for this document layout.")

        return best_parser

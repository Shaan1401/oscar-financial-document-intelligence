import re
from typing import List, Dict, Any, Optional, Tuple

class Rule:
    def __init__(
        self,
        rule_id: str,
        category: str,
        priority: int,
        match_type: str,  # "regex", "exact", "token", "contains"
        pattern: str,
        explanation: str,
        enabled: bool = True,
    ):
        self.rule_id = rule_id
        self.category = category
        self.priority = priority
        self.match_type = match_type
        self.pattern = pattern
        self.explanation = explanation
        self.enabled = enabled
        self._compiled_regex = re.compile(pattern, re.IGNORECASE) if match_type == "regex" else None

    def matches(self, text: str) -> bool:
        if not self.enabled:
            return False

        upper_text = text.upper()
        pat = self.pattern.upper()

        if self.match_type == "regex" and self._compiled_regex:
            return bool(self._compiled_regex.search(text))
        elif self.match_type == "contains":
            return pat in upper_text
        elif self.match_type == "exact":
            return pat == upper_text.strip()
        elif self.match_type == "token":
            tokens = re.split(r"[\s/\-_,.:]+", upper_text)
            return pat in tokens
        return False


class RuleEngine:
    """Configurable heuristic rule engine with priority ranking and conflict detection."""

    DEFAULT_RULES: List[Rule] = [
        # --- 1. Refunds & Reversals (Priority 100) ---
        Rule("RULE-REFUND-01", "Refunds & Reversals", 100, "regex", r"\b(REFUND|REVERSAL|REV|CASHBACK|RTN|CHARGEBACK)\b", "Contains refund or reversal keyword"),

        # --- 2. Salary & Income (Priority 95) ---
        Rule("RULE-SALARY-01", "Salary & Income", 95, "regex", r"\b(SALARY|PAYROLL|STIPEND|BONUS|DIVIDEND|INT\.?\s*PD|INTEREST\s*CREDIT)\b", "Recognized payroll or interest income keyword"),

        # --- 3. ATM / Cash Withdrawal (Priority 90) ---
        Rule("RULE-ATM-01", "ATM / Cash Withdrawal", 90, "regex", r"\b(ATM\s*WDL|ATM\s*CASH|CASH\s*WDL|NFS\s*WDL|CASH\s*WITHDRAWAL)\b", "ATM cash withdrawal narration"),

        # --- 4. Banking Charges (Priority 90) ---
        Rule("RULE-CHARGES-01", "Banking Charges", 90, "regex", r"\b(CHRG|CHARGES|SERVICE\s*TAX|GST\s*ON|ANNUAL\s*FEE|SMS\s*ALERT|MIN\s*BAL|PENALTY)\b", "Standard bank service fee or regulatory tax"),

        # --- 5. EMI & Loans (Priority 85) ---
        Rule("RULE-EMI-01", "EMI & Loans", 85, "regex", r"\b(EMI|LOAN|AUTO\s*DEBIT\s*LOAN|BAJAJ\s*FIN|HDFC\s*LOAN|ICICI\s*LOAN|HOME\s*LOAN)\b", "Loan recovery or EMI auto-debit pattern"),

        # --- 6. Tax & Government (Priority 85) ---
        Rule("RULE-TAX-01", "Tax & Government", 85, "regex", r"\b(INCOME\s*TAX|TDS|CHALLAN\s*280|ADVANCE\s*TAX|GST\s*PAYMENT|PROPERTY\s*TAX|MUNICIPAL)\b", "Direct tax, GST, or government challan payment"),

        # --- 7. Investments (Priority 80) ---
        Rule("RULE-INVEST-01", "Investments", 80, "regex", r"\b(ZERODHA|GROWW|UPSTOX|MUTUAL\s*FUND|KFINTECH|CAMS|NPS|PPF|FD\s*BOOKING|SECURITIES)\b", "Capital market broker, mutual fund registrar, or deposit"),

        # --- 8. Insurance (Priority 80) ---
        Rule("RULE-INSUR-01", "Insurance", 80, "regex", r"\b(LIC|HDFC\s*LIFE|ICICI\s*PRU|STAR\s*HEALTH|MAX\s*BUPA|CARE\s*HEALTH|INSURANCE|PREMIUM)\b", "Recognized life or general insurance company"),

        # --- 9. Utilities (Priority 80) ---
        Rule("RULE-UTIL-01", "Utilities", 80, "regex", r"\b(BESCOM|TANGEDCO|MAHAVITARAN|TATA\s*POWER|ADANI\s*ELECTRICITY|IGL|AIRTEL|JIO|VODAFONE|ACT\s*FIBERNET|ELECTRICITY|BROADBAND)\b", "Utility electricity, gas, or telecommunication biller"),

        # --- 10. Rent & Housing (Priority 75) ---
        Rule("RULE-RENT-01", "Rent & Housing", 75, "regex", r"\b(HOUSE\s*RENT|RENT\s*FOR|SOCIETY\s*MAINTENANCE|FLAT\s*MAINTENANCE|NOBROKER\s*RENT)\b", "Residential rent or apartment maintenance"),

        # --- 11. Food & Dining (Priority 75) ---
        Rule("RULE-FOOD-01", "Food & Dining", 75, "regex", r"\b(ZOMATO|SWIGGY|DOMINOS|MCDONALDS|STARBUCKS|BURGER\s*KING|PIZZA\s*HUT|REST\b|RESTAURANT|CAFE|DINING)\b", "Food delivery platform or restaurant chain"),

        # --- 12. Groceries (Priority 75) ---
        Rule("RULE-GROC-01", "Groceries", 75, "regex", r"\b(DMART|BIGBASKET|BLINKIT|ZEPTO|INSTAMART|NATURES\s*BASKET|SUPERMARKET|GROCERY|PROVISIONS)\b", "Grocery delivery or supermarket chain"),

        # --- 13. Shopping (Priority 70) ---
        Rule("RULE-SHOP-01", "Shopping", 70, "regex", r"\b(AMAZON|FLIPKART|MYNTRA|AJIO|MEESHO|NYKAA|TATA\s*CLIQ|DECATHLON|RETAIL\s*STORE|CLOTHING)\b", "E-commerce platform or apparel retailer"),

        # --- 14. Transportation & Fuel (Priority 70) ---
        Rule("RULE-TRANS-01", "Transportation & Fuel", 70, "regex", r"\b(UBER|OLA|RAPIDO|HPCL|BPCL|IOCL|SHELL|PETROL|DIESEL|METRO\s*RECHARGE|FASTAG|TOLL)\b", "Ride hailing, fuel retail pump, or toll/metro payment"),

        # --- 15. Healthcare (Priority 70) ---
        Rule("RULE-HEALTH-01", "Healthcare", 70, "regex", r"\b(APOLLO|PHARMACY|MEDPLUS|1MG|NETMEDS|HOSPITAL|CLINIC|DIAGNOSTICS|DRUG|LABS|HEALTHCARE)\b", "Pharmacy, diagnostic laboratory, or medical clinic"),

        # --- 16. Education (Priority 65) ---
        Rule("RULE-EDU-01", "Education", 65, "regex", r"\b(SCHOOL\s*FEE|COLLEGE\s*FEE|TUITION|BYJUS|UNACADEMY|COURSERA|UDEMY|UNIVERSITY|INSTITUTE)\b", "Educational institution, tuition, or e-learning service"),

        # --- 17. Entertainment (Priority 65) ---
        Rule("RULE-ENT-01", "Entertainment", 65, "regex", r"\b(NETFLIX|HOTSTAR|PRIME\s*VIDEO|SPOTIFY|BOOKMYSHOW|PVR|INOX|PLAYSTATION|STEAM\s*GAMES)\b", "Streaming subscription, cinema exhibitor, or gaming"),

        # --- 18. Travel (Priority 65) ---
        Rule("RULE-TRAVEL-01", "Travel", 65, "regex", r"\b(IRCTC|MAKEMYTRIP|EASEMYTRIP|GOIBIBO|INDIGO|AIR\s*INDIA|HOTEL|VISTARA|AIRLINE|YATRA)\b", "Train, airline, or hotel travel booking"),

        # --- 19. Transfers (Priority 50) ---
        Rule("RULE-TRSF-01", "Transfers", 50, "regex", r"\b(IMPS/P2A|NEFT/P2A|TRANSFER\s*TO|TRF\s*TO|SENT\s*TO|SELF\s*TRANSFER)\b", "Direct peer-to-peer or inter-account fund transfer"),
    ]

    def __init__(self, custom_rules: Optional[List[Rule]] = None):
        self.rules: List[Rule] = custom_rules if custom_rules is not None else list(self.DEFAULT_RULES)
        # Sort rules descending by priority
        self.rules.sort(key=lambda r: r.priority, reverse=True)

    def classify(self, description: str) -> Optional[Dict[str, Any]]:
        """
        Evaluates description against rules.
        Detects conflicts if multiple rules with highest priority match different categories.
        Returns:
          {
            "category": str,
            "rule_id": str,
            "explanation": str,
            "has_conflict": bool,
            "conflicting_rules": List[str],
          }
        or None if no rules match.
        """
        matches: List[Rule] = [r for r in self.rules if r.matches(description)]
        if not matches:
            return None

        # Check top priority group
        highest_priority = matches[0].priority
        top_matches = [m for m in matches if m.priority == highest_priority]
        unique_categories = {m.category for m in top_matches}

        if len(unique_categories) > 1:
            # Rule conflict detected!
            categories_str = ", ".join(unique_categories)
            rule_ids = [m.rule_id for m in top_matches]
            return {
                "category": "Other / Unclassified",
                "rule_id": "CONFLICT",
                "explanation": f"Conflicting rule matches found across categories: {categories_str} (Rules: {', '.join(rule_ids)})",
                "has_conflict": True,
                "conflicting_rules": rule_ids,
            }

        chosen = top_matches[0]
        return {
            "category": chosen.category,
            "rule_id": chosen.rule_id,
            "explanation": chosen.explanation,
            "has_conflict": False,
            "conflicting_rules": [],
        }

    def get_all_rules(self) -> List[Dict[str, Any]]:
        return [
            {
                "rule_id": r.rule_id,
                "category": r.category,
                "priority": r.priority,
                "match_type": r.match_type,
                "pattern": r.pattern,
                "explanation": r.explanation,
                "enabled": r.enabled,
            }
            for r in self.rules
        ]


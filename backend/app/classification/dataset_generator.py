import csv
import random
from pathlib import Path
from typing import List, Dict

RANDOM_SEED = 42

CATEGORY_MERCHANT_TEMPLATES: Dict[str, Dict[str, List[str]]] = {
    "Salary & Income": {
        "merchants": [
            "TATA CONSULTANCY SERVICES CORP ACCOUNTS", "INFOSYS TECHNOLOGIES LTD PAYROLL",
            "WIPRO ENTERPRISES SALARY DISBURSEMENT", "HCL TECHNOLOGIES LTD SALARY",
            "ACCENTURE SOLUTIONS INDIA PVT LTD", "COGNIZANT TECH SOLUTIONS SALARY",
            "TECH MAHINDRA LTD PAYROLL DISPATCH", "AMAZON DEVELOPMENT CENTRE INDIA SALARY",
            "MICROSOFT INDIA R&D PAYROLL", "GOOGLE INDIA TECH SERVICES SALARY",
            "L&T INFOTECH CORPORATE SALARY", "RELIANCE INDUSTRIES LTD PAYROLL",
            "HDFC BANK LTD INTEREST CREDIT", "ICICI BANK SAVINGS INT CAPITALISED",
            "SBI QUARTERLY SAVINGS BANK INTEREST", "KOTAK MAHINDRA INT CREDIT",
        ],
        "patterns": [
            "SALARY CREDIT - {m}", "NEFT CR-{m}-MONTHLY SALARY",
            "ACH CR-{m}-PAYROLL OCT 2026", "SALARY DISBURSEMENT {m}",
            "DIRECT CREDIT PAYROLL {m}", "{m} NET SALARY",
        ],
    },
    "Food & Dining": {
        "merchants": [
            "ZOMATO RESTAURANT ORDER", "SWIGGY BANGALORE DELIVERY", "DOMINOS PIZZA OUTLET",
            "MCDONALDS FAMILY RESTAURANT", "STARBUCKS COFFEE ROASTERY", "BURGER KING OUTLET",
            "PIZZA HUT RESTAURANT", "HALDIRAMS SWEETS & RESTAURANT", "BARBEQUE NATION BUFFET",
            "CHAAYOS TEA LOUNGE CAFE", "CHAI POINT RETAIL STORE", "SUBWAY SANDWICHES",
            "PARADISE BIRYANI RESTAURANT", "SAGAR RATNA VEG RESTAURANT", "THE BELGIAN WAFFLE CO",
        ],
        "patterns": [
            "UPI/{m}/ORDER-{r}", "POS DEBIT-{m}-{c}", "UPI/{m}@okaxis",
            "{m} DINE IN TXN", "E-COMM-{m} REF {r}", "DEBIT CARD {m} {c}",
        ],
    },
    "Groceries": {
        "merchants": [
            "DMART SUPERMARKET", "BIGBASKET PROVISIONS ONLINE", "BLINKIT QUICK COMMERCE",
            "ZEPTO 10 MIN GROCERY", "SWIGGY INSTAMART ESSENTIALS", "NATURES BASKET DELI",
            "RELIANCE FRESH VEG STORE", "RELIANCE SMART BAZAAR", "MORE SUPERMARKET RETAIL",
            "SPENCERS RETAIL GROCERY", "RATNADEEP SUPERMARKET", "LULU HYPERMARKET",
            "DUNZO DAILY GROCERIES", "COUNTRY DELIGHT MILK & DAIRY", "AMUL DAIRY PARLOUR",
        ],
        "patterns": [
            "POS {m} {c}", "UPI/{m}/BILL-{r}", "{m} STORE PURCHASES",
            "UPI/PAYTO/{m}@{b}", "DEBIT PURCHASE AT {m}", "{m} RETAIL OUTLET",
        ],
    },
    "Shopping": {
        "merchants": [
            "AMAZON SELLER SERVICES INDIA", "FLIPKART INTERNET PVT LTD", "MYNTRA DESIGNS APPAREL",
            "AJIO ONLINE FASHION STORE", "MEESHO SUPPLY CHAIN MARKETPLACE", "NYKAA BEAUTY & WELLNESS",
            "TATA CLIQ LUXURY RETAIL", "DECATHLON SPORTS INDIA", "ZARA RETAIL CLOTHING STORE",
            "H&M HENNES & MAURITZ FASHION", "CROMA ELECTRONICS STORE", "RELIANCE DIGITAL APPLIANCES",
            "SHOPPERS STOP RETAIL", "LIFESTYLE INTERNATIONAL", "UNIQLO INDIA APPAREL",
        ],
        "patterns": [
            "E-COMM/{m}/ORD-{r}", "UPI/{m}/SHOPPING", "POS TXN {m} {c}",
            "DEBIT CARD PURCHASE {m}", "PG/{m}/ORDER REF {r}", "{m} INTERNET TXN",
        ],
    },
    "Transportation & Fuel": {
        "merchants": [
            "UBER INDIA SYSTEMS PVT LTD", "OLA CABS MOBILITY RIDES", "RAPIDO BIKE TAXI",
            "HPCL PETROL PUMP STATION", "BPCL AUTO FUEL DISPENSARY", "IOCL INDIAN OIL PETROL",
            "SHELL HIGHWAY FUEL STATION", "DELHI METRO RAIL CORP SMART RECHARGE",
            "BANGALORE METRO BMRCL CARD", "MUMBAI METRO SMART RECHARGE",
            "IHMCL NHAI FASTAG TOLL RECHARGE", "PAYTM FASTAG ELECTRONIC TOLL PLAZA",
            "MERU CABS AIRPORT TRANSFER", "BLUSMART MOBILITY EV CAB", "REDましBUS INTERCITY TICKETS",
        ],
        "patterns": [
            "UPI/{m}/RIDE-{r}", "POS {m} STATION {c}", "AUTO TOLL {m} PLAZA",
            "CARD DEBIT AT {m}", "{m} COMMUTE FARE", "UPI/{m}@icici",
        ],
    },
    "Utilities": {
        "merchants": [
            "BESCOM BENGALURU ELECTRICITY BILL", "TANGEDCO CHENNAI POWER DISTRIBUTION",
            "MAHAVITARAN MAHARASHTRA POWER", "TATA POWER DELHI DISTRIBUTION",
            "ADANI ELECTRICITY MUMBAI BILL", "INDRAPRASTHA GAS LTD IGL PIPED",
            "MAHANAGAR GAS LTD MGL PIPED", "AIRTEL BROADBAND & POSTPAID BILL",
            "JIO FIBER BROADBAND SERVICES", "VODAFONE IDEA VI POSTPAID RECHARGE",
            "ACT FIBERNET BROADBAND BILL", "BANGALORE BWSSB WATER SUPPLY BILL",
            "DELHI JAL BOARD WATER UTILITY", "DISHTV DTH RECHARGE SERVICE", "TATA PLAY DTH SUBSCRIPTION",
        ],
        "patterns": [
            "BILLDESK/{m}/BILL-{r}", "BBPS/{m}/CONSUMER NO {r}",
            "UPI/{m}@billdesk", "AUTO PAY {m}", "NETBANKING BILL PAYMENT {m}",
        ],
    },
    "Healthcare": {
        "merchants": [
            "APOLLO PHARMACY HEALTHCARE", "MEDPLUS PHARMACY MEDICINES", "TATA 1MG HEALTHCARE LABS",
            "NETMEDS ONLINE PHARMACY", "PHARMEASY DIAGNOSTICS & DRUGS", "FORTIS HEALTHCARE HOSPITALS",
            "MAX SUPER SPECIALITY HOSPITAL", "MANIPAL HOSPITAL BILLING", "LAL PATHLABS CLINICAL DIAGNOSTICS",
            "SRL DIAGNOSTICS PATHOLOGY", "METROPOLIS HEALTHCARE LAB", "PRACTO CONSULTATION APPOINTMENT",
            "ASTER CMI HOSPITAL MEDICAL", "MEDANTA THE MEDICITY GURGAON", "NARAYANA HRUDAYALAYA HOSPITALS",
        ],
        "patterns": [
            "POS {m} {c}", "UPI/{m}/INVOICE-{r}", "DEBIT CARD {m}",
            "{m} MEDICAL CONSULTATION", "HOSPITAL DISCHARGE BILL {m}",
        ],
    },
    "Rent & Housing": {
        "merchants": [
            "HOUSE RENT TO LANDLORD", "NOBROKER RENT PAYMENT SERVICE", "CRED RENT PAY HOUSING",
            "MAGICBRICKS RENT DISBURSEMENT", "HOUSING.COM RENT PAYMENT", "BRIGADE RESIDENCY SOCIETY MAINTENANCE",
            "PRESTIGE APARTMENTS OWNERS ASSOCIATION", "DLF RESIDENTS WELFARE ASSOCIATION",
            "PURVANKARA FLATS MAINTENANCE BILL", "SOBHA DEVELOPERS MAINTENANCE CHARGES",
            "SOCIETY QUARTERLY MAINTENANCE FUND", "GODREJ PROPERTIES APARTMENT CHARGES",
        ],
        "patterns": [
            "NEFT OUT-{m}", "UPI/{m}/MONTHLY RENT", "IMPS/P2A/{m}",
            "RENT FOR RESIDENCE {m}", "SOCIETY DUES PAID TO {m}",
        ],
    },
    "Education": {
        "merchants": [
            "DELHI PUBLIC SCHOOL DPS TUITION", "RYAN INTERNATIONAL SCHOOL ANNUAL FEES",
            "DAV PUBLIC SCHOOL ADMISSION FEES", "KENDRIYA VIDYALAYA FEES PORTAL",
            "ALLEN CAREER INSTITUTE KOTA", "AAKASH EDUCATIONAL SERVICES FEES",
            "BYJUS E-LEARNING SUBSCRIPTION", "UNACADEMY PLUS SUBSCRIPTION",
            "COURSERA INC ONLINE COURSE", "UDEMY ONLINE CERTIFICATION",
            "BITS PILANI TUITION FEE BILL", "MANIPAL UNIVERSITY ACADEMIC DUES",
            "SIMPLILEARN AMERICAS COURSE", "UPGRAD EDUCATION PLATFORM",
        ],
        "patterns": [
            "BBPS/FEES/{m}/ACC-{r}", "UPI/{m}@edu", "NETBANKING PAYMENT {m}",
            "COLLEGE TUITION {m}", "ANNUAL TERM FEES {m}",
        ],
    },
    "Entertainment": {
        "merchants": [
            "NETFLIX ENTERTAINMENT SUBSCRIPTION", "DISNEY PLUS HOTSTAR ANNUAL VIP",
            "AMAZON PRIME VIDEO SUBSCRIPTION", "SPOTIFY INDIA MUSIC PREMIUM",
            "BOOKMYSHOW CINEMA TICKETS", "PVR CINEMAS ENTERTAINMENT",
            "INOX LEISURE MOVIE TICKETS", "CINEPOLIS INDIA THEATRES",
            "SONY LIV DIGITAL SUBSCRIPTION", "ZEE5 ENTERTAINMENT PLATFORM",
            "YOUTUBE PREMIUM FAMILY PLAN", "APPLE MUSIC SUBSCRIPTION",
            "PLAYSTATION NETWORK STORE", "STEAM DIGITAL GAMES PURCHASE",
        ],
        "patterns": [
            "E-COMM/{m}/SUB-{r}", "RECURRING DEBIT {m}", "UPI/{m}@yesbank",
            "DEBIT CARD PURCHASE {m}", "MEDIA STREAMING {m}",
        ],
    },
    "Travel": {
        "merchants": [
            "IRCTC RAILWAY TICKET RESERVATION", "MAKEMYTRIP INDIA AIRLINE BOOKING",
            "EASEMYTRIP TRAVEL SOLUTIONS", "GOIBIBO TRAVEL HOTEL & AIR",
            "INDIGO AIRLINES INTERGLOBE AVIATION", "AIR INDIA LTD DOMESTIC FLIGHT",
            "VISTARA TATA SIA AIRLINES", "AKASA AIR FLIGHT RESERVATION",
            "OYO ROOMS BUDGET HOTEL STAY", "TAJ HOTELS RESORTS PALACES",
            "MARRIOTT INTERNATIONAL HOTEL", "YATRA ONLINE TRAVEL PRIVATE LTD",
            "AGODA COMPANY TRAVEL LODGING", "BOOKING.COM HOTEL RESERVATION",
        ],
        "patterns": [
            "PG/{m}/BOOKING-{r}", "UPI/{m}@hdfcbank", "CARD PURCHASE AT {m}",
            "TICKETING DEBIT {m}", "AIRLINE PASSENGER TICKET {m}",
        ],
    },
    "Insurance": {
        "merchants": [
            "LIFE INSURANCE CORP OF INDIA LIC", "HDFC LIFE INSURANCE CO LTD",
            "ICICI PRUDENTIAL LIFE INSURANCE", "SBI LIFE INSURANCE PREMIUM",
            "MAX LIFE INSURANCE POLICY DEBIT", "STAR HEALTH ALLIED INSURANCE",
            "CARE HEALTH INSURANCE PREMIUM", "NIVA BUPA HEALTH INSURANCE",
            "BAJAJ ALLIANZ GENERAL INSURANCE", "TATA AIG GENERAL INSURANCE CO",
            "NEW INDIA ASSURANCE POLICY", "POLICYBAZAAR INSURANCE BROKER",
        ],
        "patterns": [
            "ACH DR/{m}/POL-{r}", "DIRECT DEBIT {m} PREMIUM", "UPI/{m}@billdesk",
            "POLICY PREMIUM PAYMENT {m}", "ANNUAL RENEWAL {m}",
        ],
    },
    "Investments": {
        "merchants": [
            "ZERODHA BROKING LTD TRADING", "GROWW NEXTBILLION TECHNOLOGY",
            "UPSTOX RKSV SECURITIES BROKING", "ANGEL ONE LTD BROKERAGE",
            "ICICI SECURITIES DIRECT EQUITY", "HDFC SECURITIES TRADING A/C",
            "KFIN TECHNOLOGIES MUTUAL FUND", "CAMS COMPUTER AGE MANAGEMENT",
            "NIPPON INDIA MUTUAL FUND SIP", "SBI MUTUAL FUND SCHEME SIP",
            "HDFC MUTUAL FUND INVESTMENT", "PARAG PARIKH FLEXI CAP FUND",
            "NATIONAL PENSION SCHEME NPS CRA", "PUBLIC PROVIDENT FUND PPF DEPOSIT",
        ],
        "patterns": [
            "ACH DR/{m}/SIP-{r}", "UPI/{m}@icici", "NETBANKING CAPITAL {m}",
            "FUNDS ALLOCATION TO {m}", "MUTUAL FUND PURCHASE {m}",
        ],
    },
    "Banking Charges": {
        "merchants": [
            "ANNUAL DEBIT CARD MAINTENANCE CHARGES", "QUARTERLY SMS ALERT CHARGES",
            "CONSOLIDATED SERVICE TAX & GST", "NON MAINTENANCE MINIMUM BALANCE PENALTY",
            "CHEQUE BOUNCE RETURN CHARGES", "OUTSTATION CHEQUE COLLECTION FEE",
            "STOP PAYMENT INSTRUCTION CHARGES", "IMPS TRANSACTION CONVENIENCE FEE",
            "NEFT RTGS CLEARING SURCHARGE", "ATM CARD RE-ISSUANCE FEE",
            "FOREIGN CURRENCY MARKUP CONVERSION FEE", "DOCUMENT RETRIEVAL CHARGES",
        ],
        "patterns": [
            "CHRG-{m}", "BANK SERVICE FEE: {m}", "DEBIT SURCHARGE {m}",
            "{m} INCL GST", "ACCOUNT PENALTY: {m}",
        ],
    },
    "ATM / Cash Withdrawal": {
        "merchants": [
            "HDFC BANK ATM CONNAUGHT PLACE", "SBI ATM BRANCH INDIRANAGAR",
            "ICICI BANK ATM BKC MUMBAI", "AXIS BANK ATM KORAMANGALA",
            "KOTAK MAHINDRA ATM AIRPORT T2", "PUNJAB NATIONAL BANK ATM",
            "BANK OF BARODA CASH DISPENSER", "CANARA BANK ATM MG ROAD",
            "UNION BANK OF INDIA ATM", "INDUSIND BANK ATM WHITEFIELD",
            "FEDERAL BANK ATM METRO STATION", "NFS CASH WITHDRAWAL NETWORK",
        ],
        "patterns": [
            "ATM CASH WDL {m}", "NFS CASH WDL {m}", "ATM WDL REF-{r} {m}",
            "SELF CASH WITHDRAWAL {m}", "BRANCH CASH OUT {m}",
        ],
    },
    "Transfers": {
        "merchants": [
            "TRANSFER TO SISTER FAMILY EXPENSES", "TRANSFER TO BROTHER COLLEGE DUES",
            "IMPS/P2A/TRANSFER TO MOTHER", "NEFT TRANSFER TO FRIEND VIKRAM",
            "P2P UPI TO ROOMMATE SPLITWISE", "PAYMENT TO MAID MONTHLY WAGES",
            "FUNDS TRANSFER TO SPOUSE ACCOUNT", "SENT TO FATHER MEDICAL EXPENSES",
            "INTER ACCOUNT SWEEP TRANSFER", "INTERNAL TRANSFER TO SAVINGS B",
        ],
        "patterns": [
            "UPI/P2P/{m}/{r}", "IMPS/OUT/{r}/{m}", "NEFT/P2A/{m}",
            "FUNDS TRF: {m}", "SENT VIA UPI TO {m}",
        ],
    },
    "Refunds & Reversals": {
        "merchants": [
            "REFUND AMAZON PAY FAILED ORDER", "REFUND FLIPKART RETURNED ITEM",
            "REVERSAL OF FAILED UPI PAYMENT", "ZOMATO CANCELLED ORDER REFUND",
            "SWIGGY RESTAURANT REJECTED REFUND", "IRCTC TICKET CANCELLATION REFUND",
            "MAKEMYTRIP FLIGHT CANCEL REFUND", "CHARGEBACK CREDIT DISPUTED TXN",
            "CASHBACK PROMOTION CREDITED", "BOOKMYSHOW EVENT CANCEL REFUND",
        ],
        "patterns": [
            "CR-{m}", "REFUND CR/{m}/TXN-{r}", "REVERSAL CREDIT: {m}",
            "DISPUTE SETTLEMENT {m}", "MERCHANT REFUND: {m}",
        ],
    },
    "EMI & Loans": {
        "merchants": [
            "HDFC BANK HOME LOAN REPAYMENT EMI", "ICICI BANK CAR LOAN AUTO DEBIT",
            "BAJAJ FINANCE CONSUMER DURABLE EMI", "SBI PERSONAL LOAN RECOVERY EMI",
            "AXIS BANK TWO WHEELER LOAN EMI", "KOTAK MAHINDRA AUTO LOAN DUES",
            "TATA CAPITAL PERSONAL LOAN EMI", "MAHINDRA FINANCE COMMERCIAL LOAN",
            "ADITYA BIRLA FINANCE LOAN DEDUCTION", "CREDIT CARD OUTSTANDING FULL EMI",
        ],
        "patterns": [
            "ACH DR/{m}/LOAN-{r}", "NACH AUTO RECOVERY {m}", "EMI REPAYMENT {m}",
            "LOAN DEBIT DUES {m}", "MONTHLY INSTALMENT {m}",
        ],
    },
    "Tax & Government": {
        "merchants": [
            "INCOME TAX SELF ASSESSMENT CHALLAN 280", "DIRECT TAX ADVANCE TAX QUARTER 2",
            "TDS TAX DEDUCTED AT SOURCE PAYMENT", "GST PORTAL MONTHLY RETURN CHALLAN",
            "MUNICIPAL PROPERTY TAX BBMP BENGALURU", "MCGM PROPERTY TAX ASSESSMENT MUMBAI",
            "TRAFFIC POLICE E-CHALLAN VIOLATION", "PASSPORT SEVA KENDRA TATKAAL FEE",
            "NATIONAL CONSUMER DISPUTE REDRESSAL", "STAMP DUTY REGISTRATION DEPT",
        ],
        "patterns": [
            "GOVT TAX/{m}/REF-{r}", "CHALLAN PAYMENT: {m}", "TAX DEPOSIT {m}",
            "DIRECT DEDUCTION {m}", "GOVERNMENT TREASURY: {m}",
        ],
    },
}

CITIES = ["MUMBAI", "DELHI", "BENGALURU", "HYDERABAD", "CHENNAI", "KOLKATA", "PUNE", "AHMEDABAD", "JAIPUR", "KOCHI"]
BANKS = ["HDFC", "SBI", "ICICI", "AXIS", "KOTAK", "PNB", "BOB"]

def generate_synthetic_dataset(output_csv_path: str | Path, samples_per_category: int = 100) -> Path:
    """Generates deterministic synthetic transaction dataset with reproducible seed."""
    output_csv_path = Path(output_csv_path)
    output_csv_path.parent.mkdir(parents=True, exist_ok=True)

    random.seed(RANDOM_SEED)
    records = []

    for category, config in CATEGORY_MERCHANT_TEMPLATES.items():
        merchants = config["merchants"]
        patterns = config["patterns"]

        for i in range(samples_per_category):
            m = random.choice(merchants)
            p = random.choice(patterns)
            r = f"{random.randint(100000, 999999)}"
            c = random.choice(CITIES)
            b = random.choice(BANKS).lower()

            desc = p.format(m=m, r=r, c=c, b=b)
            # Add occasional noise (spacing, trailing slashes, ref prefixes)
            variant = random.random()
            if variant < 0.2:
                desc = f"UPI/{desc}"
            elif variant < 0.35:
                desc = f"POS/{desc} REF#{r}"
            elif variant < 0.45:
                desc = f"{desc} /TXN-ID-{r}"

            records.append({
                "description": desc,
                "category": category,
            })

    # Shuffle deterministically
    random.shuffle(records)

    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["description", "category"])
        writer.writeheader()
        writer.writerows(records)

    return output_csv_path

if __name__ == "__main__":
    out = Path("sample_data/training/synthetic_transactions.csv")
    generate_synthetic_dataset(out, samples_per_category=100)
    print(f"Generated synthetic training dataset: {out}")


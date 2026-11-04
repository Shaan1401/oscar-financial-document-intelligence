from sqlalchemy.orm import Session
from app.database.models import Category

DEFAULT_CATEGORIES = [
    {"name": "Salary & Income", "category_type": "INCOME", "description": "Salaries, wages, consulting income, dividends, interest credits", "color_code": "#10B981", "icon_name": "wallet"},
    {"name": "Food & Dining", "category_type": "EXPENSE", "description": "Restaurants, food delivery, cafes, dine-out expenses", "color_code": "#F59E0B", "icon_name": "utensils"},
    {"name": "Groceries", "category_type": "EXPENSE", "description": "Supermarkets, daily provisions, dairy, produce", "color_code": "#84CC16", "icon_name": "shopping-cart"},
    {"name": "Shopping", "category_type": "EXPENSE", "description": "E-commerce, apparel, electronics, retail purchases", "color_code": "#EC4899", "icon_name": "shopping-bag"},
    {"name": "Transportation & Fuel", "category_type": "EXPENSE", "description": "Fuel stations, cabs, metro, tolls, vehicle maintenance", "color_code": "#3B82F6", "icon_name": "car"},
    {"name": "Utilities", "category_type": "EXPENSE", "description": "Electricity, water, gas, broadband, mobile recharges", "color_code": "#06B6D4", "icon_name": "zap"},
    {"name": "Healthcare", "category_type": "EXPENSE", "description": "Hospitals, pharmacies, medical tests, consultations", "color_code": "#EF4444", "icon_name": "activity"},
    {"name": "Rent & Housing", "category_type": "EXPENSE", "description": "House rent, society maintenance, home repairs", "color_code": "#8B5CF6", "icon_name": "home"},
    {"name": "Education", "category_type": "EXPENSE", "description": "School/college fees, books, online courses, training", "color_code": "#6366F1", "icon_name": "book-open"},
    {"name": "Entertainment", "category_type": "EXPENSE", "description": "OTT subscriptions, movies, gaming, events", "color_code": "#D946EF", "icon_name": "film"},
    {"name": "Travel", "category_type": "EXPENSE", "description": "Flight/train bookings, hotels, vacations", "color_code": "#14B8A6", "icon_name": "plane"},
    {"name": "Insurance", "category_type": "EXPENSE", "description": "Life, health, and vehicle insurance premiums", "color_code": "#0EA5E9", "icon_name": "shield"},
    {"name": "Investments", "category_type": "TRANSFER", "description": "Mutual funds, stocks, fixed deposits, crypto", "color_code": "#22C55E", "icon_name": "trending-up"},
    {"name": "Banking Charges", "category_type": "CHARGES", "description": "Service charges, SMS fees, card annual fees, penalties", "color_code": "#64748B", "icon_name": "credit-card"},
    {"name": "ATM / Cash Withdrawal", "category_type": "EXPENSE", "description": "ATM cash withdrawals, branch cash out", "color_code": "#78716C", "icon_name": "dollar-sign"},
    {"name": "Transfers", "category_type": "TRANSFER", "description": "Inter-account transfers, peer-to-peer payments", "color_code": "#6D28D9", "icon_name": "repeat"},
    {"name": "Refunds & Reversals", "category_type": "INCOME", "description": "Merchant refunds, failed transaction reversals, cashbacks", "color_code": "#059669", "icon_name": "rotate-ccw"},
    {"name": "EMI & Loans", "category_type": "EXPENSE", "description": "Home loan, car loan, personal loan, credit card EMIs", "color_code": "#B91C1C", "icon_name": "landmark"},
    {"name": "Tax & Government", "category_type": "EXPENSE", "description": "Income tax, GST, municipal property taxes, challans", "color_code": "#475569", "icon_name": "file-text"},
    {"name": "Other / Unclassified", "category_type": "EXPENSE", "description": "Transactions requiring review or unclassified", "color_code": "#94A3B8", "icon_name": "help-circle"},
]

def seed_categories(db: Session):
    for cat_data in DEFAULT_CATEGORIES:
        existing = db.query(Category).filter(Category.name == cat_data["name"]).first()
        if not existing:
            cat = Category(**cat_data)
            db.add(cat)
    db.commit()

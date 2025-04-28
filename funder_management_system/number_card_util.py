import frappe
from datetime import date
from collections import Counter

@frappe.whitelist()
def get_conversion_rate_by_fy(financial_year=None):
    if not financial_year:
        today = date.today()
        year = today.year
        month = today.month

        # If current month is Jan-Mar, we're in the tail end of the previous FY
        if month < 4:
            financial_year = f"{year-1}-{str(year)[-2:]}"
        else:
            financial_year = f"{year}-{str(year+1)[-2:]}"  # e.g., 2025-26

    total = frappe.db.count("Organisation Lead", {
        "financial_year_of_reachout": financial_year
    })

    confirmed = frappe.db.count("Organisation Lead", {
        "financial_year_of_reachout": financial_year,
        "lead_stage": "Confirmed Lead"
    })

    rate = (confirmed / total * 100) if total else 0

    return {
        "value": f"{rate:.2f}",
        "fieldtype": "Percent",
        "description": "Conversion Rate",
        "indicator": "Green" if rate >= 50 else "Orange",
        "confirmed": confirmed,
        "financial_year": financial_year
    }

@frappe.whitelist()
def get_churn_rate_fy(financial_year=None):
    if not financial_year:
        today = date.today()
        year = today.year
        month = today.month

        # If current month is Jan-Mar, we're in the tail end of the previous FY
        if month < 4:
            financial_year = f"{year-1}-{str(year)[-2:]}"
        else:
            financial_year = f"{year}-{str(year+1)[-2:]}"  # e.g., 2025-26

    total = frappe.db.count("Organisation Lead", {
        "financial_year_of_reachout": financial_year
    })
    
    churn_leads = frappe.db.count("Organisation Lead", {
        "financial_year_of_reachout": financial_year,
        "lead_stage": ["in", ["Cold Lead", "Dropped Lead"]]
    })
    
    churn_rate = (churn_leads / total * 100) if total else 0
    
    return {
        "value": f"{churn_rate:.2f}",
        "fieldtype": "Percent",
        "description": "Conversion Rate",
        "indicator": "Green" if churn_rate >= 50 else "Orange",
        "churn": churn_leads,
        "financial_year": financial_year
    }

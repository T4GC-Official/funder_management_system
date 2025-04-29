import frappe
from funder_management_system.utils import get_current_financial_year


@frappe.whitelist()
def get_conversion_rate_by_fy(financial_year=None):
    if not financial_year:
        financial_year = get_current_financial_year()

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
        "fieldtype": "Percent"
    }


@frappe.whitelist()
def get_churn_rate_fy(financial_year=None):
    if not financial_year:
        financial_year = get_current_financial_year()

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
        "fieldtype": "Percent"
    }

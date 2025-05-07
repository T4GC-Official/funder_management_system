import frappe
from funder_management_system.utils import get_current_financial_year, total_conversion


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


@frappe.whitelist()
def get_total_funds_received_current_fy():
    current_fy = get_current_financial_year()

    total = frappe.db.sql("""
    SELECT SUM(tranche_amount)
    FROM `tabTranche Details`
    WHERE tranche_status IN ('Received - On Time', 'Received - Delayed')
      AND tranche_financial_year = %s
    """, (current_fy,))[0][0] or 0

    return total_conversion(total)
        

 

@frappe.whitelist()
def get_total_expenditure_current_fy():
    current_fy = get_current_financial_year()
    total = frappe.db.sql("""
    SELECT SUM(utilised_amount)
    FROM `tabExpense Item`
    WHERE docstatus=1 AND financial_year = %s
    """, (current_fy,))[0][0] or 0
    
    return total_conversion(total)

@frappe.whitelist()
def get_total_active_donors_current_fy():
    current_fy = get_current_financial_year()

    start_year = int(current_fy.split('-')[0])
    fy_start = frappe.utils.getdate(f"{start_year}-04-01")
    fy_end = frappe.utils.getdate(f"{start_year + 1}-03-31")

    total = frappe.db.sql("""
        SELECT COUNT(DISTINCT donor_name)
        FROM `tabGrant Agreement` 
        WHERE grant_agreement_start_date <= %s
          AND grant_agreement_end_date >= %s
    """, (fy_end, fy_start))[0][0] or 0

    return {
        "value": total,
        "label": "Active Donors",
        "fieldtype": "Int"
    }

@frappe.whitelist()
def get_total_active_grant_agreements_current_fy():
    current_fy = get_current_financial_year()

    start_year = int(current_fy.split('-')[0])
    fy_start = frappe.utils.getdate(f"{start_year}-04-01")
    fy_end = frappe.utils.getdate(f"{start_year + 1}-03-31")

    total = frappe.db.sql("""
        SELECT COUNT(*)
        FROM `tabGrant Agreement`
        WHERE grant_agreement_start_date <= %s AND grant_agreement_end_date >= %s
    """, (fy_end, fy_start))[0][0] or 0

    return {
        "value": total,
        "label": "Active Grant Agreements",
        "fieldtype": "Int"
    }

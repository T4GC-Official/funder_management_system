import frappe

from datetime import datetime

def create_financial_year():
    current_year = datetime.now().year
    start_year = current_year - 3
    end_year = current_year + 5

    for year in range(start_year, end_year+1):
        financial_year = f"{year}-{str(year+1)[-2:]}"

        if not frappe.db.exists("Financial Year", financial_year):
            doc = frappe.get_doc({
                "doctype": "Financial Year",
                "financial_year": financial_year
            })
            doc.insert(ignore_permissions=True)

    frappe.db.commit()
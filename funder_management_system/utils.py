import frappe
from datetime import datetime

def create_financial_year():
    current_year = datetime.now().year
    start_year = current_year - 5
    end_year = current_year + 5

    for year in range(start_year, end_year + 1):
        financial_year = f"{year}-{str(year + 1)[-2:]}"
        start_date = f"{year}-04-01"
        end_date = f"{year + 1}-03-31"

        if not frappe.db.exists("Financial Year", financial_year):
            doc = frappe.get_doc({
                "doctype": "Financial Year",
                "financial_year": financial_year,
                "year_start_date": start_date,
                "year_end_date": end_date
            })
            doc.insert(ignore_permissions=True)

    frappe.db.commit()


def set_currency_permission():
    doctype = "Currency"
    role = "Fundraising Admin"
    
    existing_permissions = frappe.get_all(
        "Custom DocPerm",
        filters={"parent": doctype, "role": role},
        fields=["name"]
    )

    if existing_permissions:
        # Update the existing permission instead of adding a new one
        for perm in existing_permissions:
            docperm = frappe.get_doc("Custom DocPerm", perm.name)
            docperm.read = 1
            docperm.write = 1
            docperm.create = 1
            docperm.delete = 1
            docperm.save(ignore_permissions=True)
        frappe.msgprint(f"Updated existing permissions for {role} on {doctype}")
    else:
        # If no existing permission, append a new one
        currency_doc = frappe.get_doc("DocType", doctype)
        currency_doc.append("permissions", {
            "role": role,
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
        })
        currency_doc.save()
        frappe.msgprint(f"Added new permissions for {role} on {doctype}")

    frappe.db.commit()
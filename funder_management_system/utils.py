import frappe, json
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
    
def set_currency_permission_using_custom():
    """Set or update Currency DocType permissions for Fundraising Admin role."""
    doctype = "Currency"
    role = "Fundraising Admin"

    try:
        existing_permissions = frappe.get_all(
            "Custom DocPerm",
            filters={"parent": doctype, "role": role},
            fields=["name"]
        )

        if existing_permissions:
            # Update existing permissions
            for perm in existing_permissions:
                docperm = frappe.get_doc("Custom DocPerm", perm.name)
                docperm.read = 1
                docperm.write = 1
                docperm.create = 1
                docperm.delete = 1
                docperm.save(ignore_permissions=True)
            frappe.msgprint(f"Updated existing permissions for {role} on {doctype}")
        else:
            # Create a new Custom DocPerm entry
            custom_perm = frappe.get_doc({
                "doctype": "Custom DocPerm",
                "parent": doctype,
                "parenttype": "DocType",
                "parentfield": "permissions",
                "role": role,
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1
            })
            custom_perm.insert(ignore_permissions=True)
            frappe.msgprint(f"Added new permissions for {role} on {doctype}")

        frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"Error setting permissions for {role} on {doctype}: {e}")
    
    
     
def skip_setup_wizard():
    """Automatically skip the setup wizard after install."""
    frappe.db.set_value("System Settings", "System Settings", "setup_complete", 1)
    frappe.db.commit()
    print("Setup wizard skipped!")


def set_default_workspace(doc, method):
    """Set default workspace for new users"""
    if not doc.default_workspace:  # Only set if not already defined
        doc.default_workspace = "Main Workspace"
        doc.save(ignore_permissions=True)  # Correct way to update
        frappe.msgprint(f"Default workspace set to 'Main Workspace' for {doc.name}")

    

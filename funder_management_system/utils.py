import frappe, json
from datetime import datetime, date
from frappe.share import set_permission

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
            print(f"Updated existing permissions for {role} on {doctype}")
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
            print(f"Added new permissions for {role} on {doctype}")

        frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"Error setting permissions for {role} on {doctype}: {e}")
    
    
# write a generic function to add data import permission on FMS doctypes the user will pass the doctype name and the role name
def set_import_permission(doctype, role, permissions):
    try:
        existing_perm = frappe.get_all("Custom DocPerm", 
                                       filters={"parent": doctype, "role": role}, 
                                       fields=["name"])
        if not existing_perm:
            custom_perm = frappe.get_doc({
                "doctype": "Custom DocPerm",
                "parent": doctype,
                "parenttype": "DocType",
                "parentfield": "permissions",
                "role": role,
                "read": 1 if "read" in permissions else 0,
                "write": 1 if "write" in permissions else 0,
                "create": 1 if "create" in permissions else 0,
                "delete": 1 if "delete" in permissions else 0,
                "export": 1 if "export" in permissions else 0,
                "import": 1 if "import" in permissions else 0
            })
            custom_perm.insert(ignore_permissions=True)
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

    
def enable_permission_for_fms_roles(fms_admin=True):
    if not fms_admin:
        return

    roles = ["Fundraising Admin"]
    permissions_map = {
        "Page": ["read"],
        "Data Import": ["read", "write", "create", "delete"],
        "Data Export": ["read", "write"],
        "Error Log": ["read", "write"],
    }

    for doctype, permissions in permissions_map.items():
        for role in roles:
            set_import_permission(doctype, role, permissions)

    frappe.db.commit()
    print(f"Permissions set for FMS roles{roles}")


def share_custom_number_cards_with_everyone():
    cards = ["Churn Rate", "Conversion Rate"]

    for card in cards:
        try:
            set_permission(
                doctype="Number Card",
                name=card,
                user=None,           
                permission_to="read",
                value=1,
                everyone=1
            )
            frappe.db.commit()
            print(f"Shared {card} with everyone.")
        except Exception as e:
            frappe.log_error(title="Failed to Share Number Card with Everyone", message=f"{card}: {str(e)}")

def get_current_financial_year():
    today = date.today()
    year = today.year
    month = today.month

    # If current month is Jan-Mar, we're in the tail end of the previous FY
    if month < 4:
        financial_year = f"{year-1}-{str(year)[-2:]}"
    else:
        financial_year = f"{year}-{str(year+1)[-2:]}"  # e.g., 2025-26

    return financial_year
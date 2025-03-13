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


def set_currency_permission():
    try:
        frappe.flags.in_developer_mode = 1 
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
    except Exception as e:
        print(f"Error while setting currency permissions: {e}")
    finally:
        frappe.flags.in_developer_mode = 1 
    
def enable_developer_mode():
    """Enable Developer Mode in site_config.json."""
    try:
        site_config_path = frappe.get_site_path("site_config.json")

        with open(site_config_path, "r+") as f:
            site_config = json.load(f)
            original_developer_mode = site_config.get("developer_mode", 0)
            site_config["developer_mode"] = 1
            f.seek(0)
            json.dump(site_config, f, indent=4)
            f.truncate()
        frappe.msgprint("Developer Mode enabled")
        return original_developer_mode 
    except Exception as e:
        print(f"Error while enabling developer mode: {e}")
    finally:
        return original_developer_mode  # Return original state to restore later

def disable_developer_mode():
    """Restore Developer Mode to its original state."""
    try:
        #fetch original state from site_config_backup_file file from the site path directory 
        original_state = json.load(open(frappe.get_site_path("site_config_backup.json")))
        site_config_path = frappe.get_site_path("site_config.json")

        with open(site_config_path, "r+") as f:
            site_config = json.load(f)
            site_config["developer_mode"] = original_state  # Restore previous state
            f.seek(0)
            json.dump(site_config, f, indent=4)
            f.truncate()
    except Exception as e:
        print(f"Error while disabling developer mode: {e}")
    finally:
        pass
    
def set_currency_permission_using_custom():
    """Set or update Currency DocType permissions for Fundraising Admin role."""
    doctype = "Currency"
    role = "Fundraising Admin"

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

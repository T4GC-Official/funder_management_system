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
    cards = ["Churn Rate In Current Financial Year", 
             "Conversion Rate in Current Financial Year",
             "Total Active Donors - Current FY",
             "Total Active Grant Agreements - Currrent FY",
             "Total Funds Received - Current FY",
             "Total Expenses - Current FY"]
    

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

def update_settings():
   
    """
    Set up website customizations.

    This function sets up various website customizations, such as the app name,
    title prefix, app logo, home page, disable signup, and footer options.

    It also sets up system settings, such as denying multiple sessions,
    session expiry, allowed file extensions, max file size, and other options.

    Finally, it sets up navbar settings.

    If any of these updates fail, the function logs an error and prints a
    message indicating failure.
    """
    image_loc = "https://static.wixstatic.com/media/7dc063_4079a88b01c54ab1a2a5cb6580e028a7~mv2.png/v1/fill/w_180,h_188,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/T4G_Website_Logo_edited.png"
    
    try:
        # Website Settings
        website_settings = frappe.get_single("Website Settings")
        website_settings.app_name = "Fundraising Management System"
        website_settings.title_prefix = "Fundraising Management System"
        website_settings.app_logo = image_loc
        website_settings.home_page = "/app/main-workspace"
        website_settings.disable_signup = 1
        website_settings.show_footer_on_login = 1
        website_settings.banner_image = image_loc
        website_settings.splash_image = image_loc
        website_settings.favicon = image_loc
        website_settings.copyright = "Tech4Good Community"
        website_settings.footer_powered = "Fundraising Management System"
        website_settings.save()
        print("Website Settings updated.")

        # System Settings
        system_settings = frappe.get_single("System Settings")
        system_settings.deny_multiple_sessions = 1
        system_settings.session_expiry = "24:00"
        system_settings.allowed_file_extensions = "csv,jpg,png,svg,pdf,gif"
        system_settings.max_file_size = 5
        system_settings.allow_error_traceback = 0
        system_settings.login_with_email_link = 0
        system_settings.save()
        print("System Settings updated.")

        # Navbar Settings
        try:
            navbar_settings = frappe.get_single("Navbar Settings")
            navbar_settings.app_logo = image_loc
            navbar_settings.save()
            print("Navbar Settings updated.")
        except Exception:
            print("Navbar Settings doctype not found or update failed.")

        frappe.db.commit()
        print("All settings updated and committed successfully.")

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Website Settings Setup Failed")
        print("Failed to update settings. Check error logs.")


def total_conversion(total: float) -> dict:
    """
    Format the total conversion value into a human-readable format.
    """
    if total is None:
        return {
            "value": "0.00",
            "fieldtype": "Data"
        }
    if total >= 10000000:
        formatted_total = f"{total / 10000000:.2f}Cr"
    elif total >= 100000:
        formatted_total = f"{total / 100000:.2f}L"
    else:
        formatted_total = f"{total:.2f}"
    return {
        "value": formatted_total,
        "fieldtype": "Data"
    }
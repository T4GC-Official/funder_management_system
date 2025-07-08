import frappe
import json
from frappe import _
from datetime import datetime, date
from frappe.share import set_permission
from .role_management import create_roles_if_missing, patch_roles_with_default_app


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


def add_permissions(role, doctype, permissions, permlevel=0):
    """
    Adds specified permissions to a role on a given Doctype using Custom DocPerm.

    :param role: str, role name
    :param doctype: str, target doctype to add permission on
    :param permissions: dict, permission flags like {"read": 1, "write": 1}
    :param permlevel: int, permission level, default is 0
    """
    # Check if a matching Custom DocPerm already exists
    filters = {
        "parent": doctype,
        "role": role,
        "permlevel": permlevel,
    }
    filters.update({key: 1 for key in permissions if key != "permlevel"})

    if frappe.get_all("Custom DocPerm", filters=filters):
        print(
            f"! Permissions already exist for role '{role}' on '{doctype}' at level {permlevel}. Skipping.")
        return

    # Insert permission
    doc = frappe.get_doc({
        "doctype": "Custom DocPerm",
        "parent": doctype,
        "parenttype": "DocType",
        "parentfield": "permissions",
        "role": role,
        "permlevel": permlevel,
        **{key: 1 for key in permissions if key != "permlevel"}
    })

    doc.insert(ignore_permissions=True)
    print(
        f"Granted {list(permissions.keys())} on '{doctype}' to role '{role}' at level {permlevel}")


def setup_fms_dashboard_permissions():
    """
    Sets up FMS-related roles and grants appropriate permissions.
    """
    fms_roles = ["Cashflow Dashboard Access",
                 "Fundraising Dashboard Access",
                 "Donor Acquisition Dashboard Access"]
    create_roles_if_missing(fms_roles)

    try:
        # Grant permissions
        permissions_map = [
           
            ("Cashflow Dashboard Access", "Financial Year", {"read": 1}),
            ("Fundraising Dashboard Access", "Financial Year", {"read": 1}),
            ("Donor Acquisition Dashboard Access", "Financial Year", {"read": 1}),
            ("Cashflow Dashboard Access", "Page", {"read": 1}),
            ("Fundraising Dashboard Access", "Page", {"read": 1}),
            ("Donor Acquisition Dashboard Access", "Page", {"read": 1}),
        ]


        for perm in permissions_map:
            if len(perm) == 3:
                role, doctype, perms = perm
                level = 0
            else:
                role, doctype, perms, level = perm
            add_permissions(role, doctype, perms, level)

    except Exception as e:
        frappe.log_error(title="FMS Permission Setup Error", message=str(e))
        print(f"Error setting up FMS permissions: {e}")

    frappe.db.commit()
    print("All FMS permissions applied successfully.")


def set_default_workspace(doc, method):
    """Set default workspace for new users"""
    if not doc.default_workspace:  # Only set if not already defined
        doc.default_workspace = "Main Workspace"
        doc.save(ignore_permissions=True)  # Correct way to update
        frappe.msgprint(
            f"Default workspace set to 'Main Workspace' for {doc.name}")



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
            frappe.log_error(
                title="Failed to Share Number Card with Everyone", message=f"{card}: {str(e)}")


@frappe.whitelist()
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
        system_settings.allowed_file_extensions = "csv\njpg\npng\nsvg\npdf\ngif"
        system_settings.max_file_size = 5
        system_settings.allow_error_traceback = 0
        system_settings.login_with_email_link = 0
        system_settings.link_field_results_limit = 50  # defalut is 10 and max is 50
        system_settings.reset_password_link_expiry_duration = "10m"  # minutes
        system_settings.enable_password_policy = 1
        system_settings.minimum_password_score = 4
        if not system_settings.language:
            system_settings.language = frappe.defaults.get_global_default(
                "language") or "en"
        if not system_settings.time_zone:
            system_settings.time_zone = frappe.defaults.get_global_default(
                "time_zone") or "Asia/Kolkata"

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
        frappe.log_error(frappe.get_traceback(),
                         "Website Settings Setup Failed")
        print(
            f"Failed to update settings. Check error logs.{frappe.get_traceback()}")


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


@frappe.whitelist()
def get_module_profile(module_profile: str):
    """Return only modules belonging to the `funder_management_system` app for the given Module Profile."""

    module_profile = frappe.get_doc(
        "Module Profile", {"module_profile_name": module_profile})

    # Get all modules allowed in this profile
    blocked_modules = module_profile.get("block_modules") or []
    allowed_modules = frappe.get_all("Module Def", filters={
        "app_name": "funder_management_system",
        "name": ["not in", blocked_modules]
    }, pluck="name")

    return allowed_modules


@frappe.whitelist()
def get_all_roles():
    """return all roles"""
    active_domains = frappe.get_active_domains()

    roles = frappe.get_all(
        "Role",
        filters={
            "name": ("not in", frappe.permissions.AUTOMATIC_ROLES),
            "disabled": 0,
        },
        or_filters={"ifnull(restrict_to_domain, '')": "",
                    "restrict_to_domain": ("in", active_domains)},
        order_by="name",
    )

    final = sorted([role.get("name") for role in roles])

    if frappe.session.user != "Administrator":
        excluded_roles = [
            "Accounts Manager",
            "Accounts User",
            "Blogger",
            "Commit Project Member",
            "Dashboard Manager",
            "Knowledge Base Contributor",
            "Knowledge Base Editor",
            "Maintenance Manager",
            "Maintenance User",
            "Marketing Manager",
            "Newsletter Manager",
            "Prepared Report User",
            "Purchase Manager",
            "Purchase Master Manager",
            "Purchase User",
            "Report Manager",
            "Sales Manager",
            "Sales Master Manager",
            "Sales User",
            "Script Manager",
            "System Manager",
            "Website Manager",
            "Workspace Manager",
            "Inbox User",
            "Translator",
        ]
        final = [role for role in final if role not in excluded_roles]

    return final


def normalize_financial_years(financial_years):
    """Helper function to parse and normalize financial_years input."""
    if not financial_years:
        return []

    if isinstance(financial_years, str):
        try:
            parsed = json.loads(financial_years)
            return parsed if isinstance(parsed, list) else [parsed]
        except json.JSONDecodeError:
            return [financial_years]

    if isinstance(financial_years, list):
        return financial_years

    return []


def get_fy_date_ranges_from_doctype(financial_years):
    """Fetch start and end dates for the given financial years from the Financial Year doctype"""
    if not financial_years:
        return []

    fy_docs = frappe.get_all(
        "Financial Year",
        filters={"name": ["in", financial_years]},
        fields=["year_start_date", "year_end_date"]
    )

    return [(d.year_start_date, d.year_end_date) for d in fy_docs]


def validate_fundraising_admin(doc, method):
    fundraising_admin_role = "Fundraising Admin"
    if doc.email == "admin1@example.com":
        return True

    new_roles = set([r.role for r in doc.roles] or [])
    if doc.is_fundraising_admin and fundraising_admin_role not in new_roles:
        frappe.msgprint(
            _("You cannot remove the Fundraising Admin role while 'Is Fundraising Admin' is checked."),
            indicator='red'
        )
        doc.append("roles", {"role": fundraising_admin_role})


@frappe.whitelist()
def get_fms_modules():
    """Return modules belonging to FMS App."""
    modules = frappe.get_all(
        "Module Def",
        filters={"app_name": "funder_management_system"},
        pluck="module_name"
    )
    return modules

@frappe.whitelist()
def limit_maximum_users(doc, method):
    max_users = int(frappe.local.conf.get("max_users", 22))
    total_users = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabUser`
        WHERE enabled = 1 and name NOT IN ('Administrator', 'Guest')
    """)[0][0]
    if total_users > max_users:
        frappe.throw(_("Maximum number of users reached. Allowed: {0}").format(max_users))


def limit_storage_quota(doc, method):
    max_storage_quota = int(frappe.local.conf.get("max_storage_quota_in_mb", 10240))
    max_storage_bytes = max_storage_quota * 1024 * 1024

    total_file_storage = frappe.db.sql("""SELECT sum(file_size) FROM `tabFile`""")[0][0]
    if total_file_storage + doc.file_size > max_storage_bytes:
        frappe.throw(_("You have reached your storage limit of {0} MB. Please delete unused files or upgrade your plan.").format(max_storage_quota))



def delete_web_pages():
    web_pages = frappe.get_all("Web Page", pluck="name")
    for page in web_pages:
        frappe.delete_doc("Web Page", page)

    frappe.db.commit()
    print("Deleted all web pages")
    
    
# write a method to delete a specific user from the system

def delete_user():
    email_address="admin1@example.com"
    """
    Deletes a user from the system based on their email address.
    
    :param email_address: str, the email address of the user to delete
    """
    if not email_address:
        print(_("Please provide the email address of the user you want to delete."))
        return

    try:
        user = frappe.db.sql("SELECT name FROM `tabUser` WHERE email = %s", email_address, as_dict=True)
        if not user:
            print(_("User with email {0} does not exist.").format(email_address))
        else:
            frappe.delete_doc("User", user[0].name)
            frappe.db.commit()
            print(f"User with email {email_address} deleted successfully.")
    except Exception as e:
        print(_("Error: {0}").format(e))

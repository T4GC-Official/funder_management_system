import frappe
from .utils import create_roles_if_missing, add_permissions


PERMISSION_SETS = {
    "full_access": {
        "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1,
        "cancel": 1, "import": 1, "export": 1, "share": 1, "email": 1, "report": 1
    },
    "view_access": {
        "read": 1, "report": 1, "export": 1
    },
    "select_read_write": {
        "read": 1, "select": 1, "write": 1,
    },
    "select_read": {
        "read": 1, "select": 1,
    },
    "select_only": {
        "select": 1},
    "report_only": {
        "report": 1},
    "perm_level_1": {
        "read": 1, "write": 1
    },
    "read_only": {
        "read": 1
    },
}


def setup_module_specific_roles():
    fms_roles = [
        "Budget Allocation Full Access",
        "Budget Allocation View Access",
        "Donor Acquisition Full Access",
        "Donor Acquisition View Access",
        "Donor Engagement Full Access",
        "Donor Engagement View Access",
        "Utilisation Module Full Access",
        "Utilisation Module View Access",
        "Org Toolkit Full Access",
        "Org Toolkit View Access",
    ]
    create_roles_if_missing(fms_roles)
    setup_budget_allocation_module_roles()
    setup_donor_acquisition_module_roles()
    setup_donor_engagement_module_roles()
    setup_utilisation_module_roles()
    setup_org_toolkit_roles()
    setup_reports_access_roles()
    setup_fms_dashboard_permissions()


def setup_budget_allocation_module_roles():

    role_doctypes_permissions_level_mapping = [
        # full access
        ("Budget Allocation Full Access", "Budget Category", "full_access", 0),
        ("Budget Allocation Full Access", "Budget Sub-Category", "full_access", 0),
        ("Budget Allocation Full Access", "Financial Year", "full_access", 0),
        ("Budget Allocation Full Access", "Currency", "full_access", 0),
        ("Budget Allocation Full Access", "Budget Plan", "full_access", 0),
        ("Budget Allocation Full Access", "Budget Plan Template", "full_access", 0),
        ("Budget Allocation Full Access", "Budget Breakdown", "full_access", 0),
        ("Budget Allocation Full Access", "Workspace", "full_access", 0),
        ("Budget Allocation Full Access", "Custom HTML Block", "full_access", 0),

        # only view access
        ("Budget Allocation View Access", "Budget Category", "view_access", 0),
        ("Budget Allocation View Access", "Budget Sub-Category", "view_access", 0),
        ("Budget Allocation View Access", "Financial Year", "view_access", 0),
        ("Budget Allocation View Access", "Currency", "view_access", 0),
        ("Budget Allocation View Access", "Budget Plan", "view_access", 0),
        ("Budget Allocation View Access", "Budget Plan Template", "view_access", 0),
        ("Budget Allocation View Access", "Budget Breakdown", "view_access", 0),
        ("Budget Allocation View Access", "Workspace", "view_access", 0),
        ("Budget Allocation View Access", "Custom HTML Block", "view_access", 0),
    ]
    try:
        for role, doctype, permission_key, permlevel in role_doctypes_permissions_level_mapping:
            add_permissions(
                role, doctype, PERMISSION_SETS[permission_key], permlevel)
    except Exception as e:
        frappe.log_error(f"Error setting up Budget Allocation roles: {e}")


def setup_donor_acquisition_module_roles():

    # format: (role, doctype, permissions, permission level)
    role_doctypes_permissions_level_mapping = [
        # full access
        ("Donor Acquisition Full Access", "Organisation Details", "full_access", 0),
        ("Donor Acquisition Full Access", "Organisation POC", "full_access", 0),
        ("Donor Acquisition Full Access",
         "Preferred Means of Communication", "full_access", 0),
        ("Donor Acquisition Full Access", "Organisation Lead", "full_access", 0),
        ("Donor Acquisition Full Access", "Compliance Checklist", "full_access", 0),
        ("Donor Acquisition Full Access", "Thematic Area", "full_access", 0),
        ("Donor Acquisition Full Access", "Source of Connection", "full_access", 0),
        ("Donor Acquisition Full Access", "Category", "full_access", 0),
        ("Donor Acquisition Full Access", "Designation", "full_access", 0),
        ("Donor Acquisition Full Access", "Designation", "select_only", 0),
        ("Donor Acquisition Full Access", "Financial Year", "select_only", 0),


        # only view access
        ("Donor Acquisition View Access", "Organisation Details", "view_access", 0),
        ("Donor Acquisition View Access", "Organisation POC", "view_access", 0),
        ("Donor Acquisition View Access",
         "Preferred Means of Communication", "view_access", 0),
        ("Donor Acquisition View Access", "Organisation Lead", "view_access", 0),
        ("Donor Acquisition View Access", "Compliance Checklist", "view_access", 0),
        ("Donor Acquisition View Access", "Thematic Area", "view_access", 0),
        ("Donor Acquisition View Access", "Source of Connection", "view_access", 0),
        ("Donor Acquisition View Access", "Category", "view_access", 0),
        ("Donor Acquisition View Access", "Designation", "view_access", 0),
        ("Donor Acquisition View Access", "Financial Year", "view_access", 0),

    ]

    try:
        for role, doctype, permission_key, permlevel in role_doctypes_permissions_level_mapping:
            add_permissions(
                role, doctype, PERMISSION_SETS[permission_key], permlevel)
    except Exception as e:
        frappe.log_error(f"Error setting up Donor Acquisition roles: {e}")


def setup_donor_engagement_module_roles():
    """
    Sets up roles and permissions for the Donor Engagement module.
    """
    # format: (role, doctype, permissions, permission level)
    role_doctypes_permissions_level_mapping = [
        # full access
        ("Donor Engagement Full Access",
         "Engagement Checklist Master", "full_access", 0),
        ("Donor Engagement Full Access", "Donor", "full_access", 0),
        ("Donor Engagement Full Access", "Engagement Checklist", "full_access", 0),
        ("Donor Engagement Full Access", "Tranche Details", "full_access", 0),
        ("Donor Engagement Full Access", "Grant Agreement", "full_access", 0),
        ("Donor Engagement Full Access", "Organisation Lead", "read_only", 0),
        ("Donor Engagement Full Access", "Organisation POC", "read_only", 0),

        # only view access
        ("Donor Engagement View Access",
         "Engagement Checklist Master", "view_access", 0),
        ("Donor Engagement View Access", "Donor", "view_access", 0),
        ("Donor Engagement View Access", "Engagement Checklist", "view_access", 0),
        ("Donor Engagement View Access", "Tranche Details", "view_access", 0),
        ("Donor Engagement View Access", "Grant Agreement", "view_access", 0),
        ("Donor Engagement View Access", "Organisation Lead", "view_access", 0),
        ("Donor Engagement View Access", "Organisation POC", "view_access", 0),

    ]

    try:
        for role, doctype, permission_key, permlevel in role_doctypes_permissions_level_mapping:
            add_permissions(
                role, doctype, PERMISSION_SETS[permission_key], permlevel)
    except Exception as e:
        frappe.log_error(f"Error setting up Donor Engagement roles: {e}")


def setup_utilisation_module_roles():
    """
    Sets up roles and permissions for the Utilisation module.
    """
    # format: (role, doctype, permissions, permission level)
    role_doctypes_permissions_level_mapping = [
        ("Utilisation Module Full Access", "Expense Item", "full_access", 0),
        ("Utilisation Module Full Access",
         "Expense Item Child Table", "full_access", 0),
        ("Utilisation Module Full Access", "Utilisation Record", "full_access", 0),
        ("Utilisation Module Full Access", "Financial Year", "select_only", 0),
        ("Utilisation Module Full Access", "Donor", "select_only", 0),
        ("Utilisation Module Full Access", "Grant Agreement", "select_read", 0),
        ("Utilisation Module Full Access", "Budget Plan", "select_only", 0),
        ("Utilisation Module Full Access", "Budget Category", "select_only", 0),
        ("Utilisation Module Full Access", "Budget Sub-Category", "select_only", 0),
        ("Utilisation Module Full Access", "Currency", "select_only", 0),
        ("Utilisation Module Full Access",
         "Engagement Checklist Master", "read_only", 0),

        ("Utilisation Module View Access", "Expense Item", "view_access", 0),
        ("Utilisation Module View Access",
         "Expense Item Child Table", "view_access", 0),
        ("Utilisation Module View Access", "Utilisation Record", "view_access", 0),
        ("Utilisation Module View Access", "Financial Year", "read_only", 0),
        ("Utilisation Module View Access", "Donor", "read_only", 0),
        ("Utilisation Module View Access", "Grant Agreement", "read_only", 0),
        ("Utilisation Module View Access", "Budget Plan", "read_only", 0),
        ("Utilisation Module View Access", "Budget Category", "read_only", 0),
        ("Utilisation Module View Access", "Budget Sub-Category", "read_only", 0),
        ("Utilisation Module View Access", "Currency", "read_only", 0),
        ("Utilisation Module View Access",
         "Engagement Checklist Master", "read_only", 0),
    ]

    try:
        for role, doctype, permission_key, permlevel in role_doctypes_permissions_level_mapping:
            add_permissions(
                role, doctype, PERMISSION_SETS[permission_key], permlevel)
    except Exception as e:
        frappe.log_error(f"Error setting up Utilisation roles: {e}")


def setup_org_toolkit_roles():
    """
    Sets up roles and permissions for the Document List module.
    """
    # format: (role, doctype, permissions, permission level)
    role_doctypes_permissions_level_mapping = [
        ("Org Toolkit Full Access", "Document List", "full_access", 0),
        ("Org Toolkit View Access", "Document List", "view_access", 0),
    ]

    try:
        for role, doctype, permission_key, permlevel in role_doctypes_permissions_level_mapping:
            add_permissions(
                role, doctype, PERMISSION_SETS[permission_key], permlevel)
    except Exception as e:
        frappe.log_error(f"Error setting up Document List roles: {e}")


def setup_reports_access_roles():
    fms_roles = [
        "Budget Plan Report Access",
        "Budget vs Utilisation Report Access",
        "Donation vs Utilisation Report Access"
    ]
    create_roles_if_missing(fms_roles)
    """
    Sets up roles and permissions for the Reports module.
    """
    # format: (role, doctype, permissions, permission level)
    role_doctypes_permissions_level_mapping = [
        ("Budget Plan Report Access", "Report", "view_access", 0),
        ("Budget Plan Report Access", "Budget Plan", "report_only", 0),
        ("Budget Plan Report Access", "Financial Year", "read_only", 0),
        ("Budget Plan Report Access", "Currency", "read_only", 0),
        
        ("Budget vs Utilisation Report Access", "Report", "view_access", 0),
        ("Budget vs Utilisation Report Access", "Expense Item", "report_only", 0),
        ("Budget vs Utilisation Report Access", "Budget Plan", "read_only", 0),
        ("Budget vs Utilisation Report Access", "Financial Year", "read_only", 0),
        ("Budget vs Utilisation Report Access", "Currency", "read_only", 0),
        
        ("Donation vs Utilisation Report Access", "Report", "view_access", 0),
        ("Donation vs Utilisation Report Access", "Donor", "report_only", 0),
        ("Donation vs Utilisation Report Access", "Financial Year", "read_only", 0),
        ("Donation vs Utilisation Report Access", "Currency", "read_only", 0),
        
        
        
    ]

    try:
        for role, doctype, permission_key, permlevel in role_doctypes_permissions_level_mapping:
            add_permissions(
                role, doctype, PERMISSION_SETS[permission_key], permlevel)
    except Exception as e:
        frappe.log_error(f"Error setting up Reports roles: {e}")
        
        
def setup_fms_dashboard_permissions():
    """
    Sets up FMS-related roles and grants appropriate permissions.
    """
    fms_roles = ["Cashflow Dashboard Access",
                 "Fundraising Dashboard Access",
                 "Donor Acquisition Dashboard Access"]
    create_roles_if_missing(fms_roles)

        # Grant permissions
    permissions_map = [
        ("Cashflow Dashboard Access", "Financial Year", "read_only", 0),
        ("Fundraising Dashboard Access", "Financial Year", "read_only", 0),
        ("Donor Acquisition Dashboard Access", "Financial Year", "read_only", 0),
        ("Cashflow Dashboard Access", "Page", "read_only", 0),
        ("Fundraising Dashboard Access", "Page", "read_only", 0),
        ("Donor Acquisition Dashboard Access", "Page", "read_only", 0),
    ]

    try:
        for role, doctype, permission_key, permlevel in permissions_map:
            add_permissions(
                role, doctype, PERMISSION_SETS[permission_key], permlevel)
    except Exception as e:
        frappe.log_error(f"Error setting up Reports roles: {e}")
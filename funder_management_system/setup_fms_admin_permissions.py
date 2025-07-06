import frappe
from .utils import create_roles_if_missing, add_permissions


def setup_modules_roles():
    """
    Sets up FMS-related roles and grants appropriate permissions.
    """
    fms_roles = ["Fundraising Adminr"]

    create_roles_if_missing(fms_roles)
    setup_budget_allocation_module_roles()
    setup_donor_acquisition_module_roles()
    setup_donor_engagement_module_roles()
    setup_utilisation_module_roles()
    setup_org_toolkit_roles()
    setup_fms_fundraising_admin_must_have_role()


def setup_budget_allocation_module_roles():

    # format: (role, doctype, permissions, permission level)
    role_doctypes_permissions_level_mapping = [

        ("Fundraising Admin", "Budget Category", {
         "read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Budget Sub-Category",
         {"read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Financial Year", {
         "read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Currency", {
         "read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Budget Plan Template", {
         "read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Budget Plan", {
         "read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1, "report": 1}, 0),
        ("Fundraising Admin", "Budget Breakdown", {
         "read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Workspace", {
         "read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Custom HTML Block", {
         "read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),


    ]

    try:
        for role, doctype, permissions, permlevel in role_doctypes_permissions_level_mapping:
            add_permissions(role, doctype, permissions, permlevel)
    except Exception as e:
        frappe.log_error(f"Error setting up FMS roles: {e}")


def setup_donor_acquisition_module_roles():

    # format: (role, doctype, permissions, permission level)
    role_doctypes_permissions_level_mapping = [

        ("Fundraising Admin", "Organisation Details", {
         "read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Organisation POC", {
         "read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Preferred Means of Communication", {
         "read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Organisation Lead", {
         "read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Compliance Checklist", {
         "read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Thematic Area", {
         "read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Source of Connection", {
         "read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Category", {
         "read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),

    ]

    try:
        for role, doctype, permissions, permlevel in role_doctypes_permissions_level_mapping:
            add_permissions(role, doctype, permissions, permlevel)
    except Exception as e:
        frappe.log_error(f"Error setting up Donor Acquisition roles: {e}")


def setup_donor_engagement_module_roles():
    """
    Sets up roles and permissions for the Donor Engagement module.
    """
    # format: (role, doctype, permissions, permission level)
    role_doctypes_permissions_level_mapping = [
        ("Fundraising Admin", "Engagement Checklist Master", {
         "read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Donor", {
         "read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Engagement Checklist", {
         "read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Tranche Details", {
         "read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Grant Agreement", {
         "read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
    ]

    try:
        for role, doctype, permissions, permlevel in role_doctypes_permissions_level_mapping:
            add_permissions(role, doctype, permissions, permlevel)
    except Exception as e:
        frappe.log_error(f"Error setting up Donor Engagement roles: {e}")


def setup_utilisation_module_roles():
    """
    Sets up roles and permissions for the Utilisation module.
    """
    # format: (role, doctype, permissions, permission level)
    role_doctypes_permissions_level_mapping = [
        ("Utilisation Module Full Access", "Expense Item",  {"read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1,
                                                             "cancel": 1, "import": 1, "export": 1, "share": 1, "email": 1, "report": 1}, 0),
        ("Utilisation Module Full Access",
         "Expense Item Child Table",  {"read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1,
                                       "cancel": 1, "import": 1, "export": 1, "share": 1, "email": 1, "report": 1}, 0),
        ("Utilisation Module Full Access", "Utilisation Record",  {"read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1,
                                                                   "cancel": 1, "import": 1, "export": 1, "share": 1, "email": 1, "report": 1}, 0),
        ("Utilisation Module Full Access", "Financial Year",  {"read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1,
                                                               "cancel": 1, "import": 1, "export": 1, "share": 1, "email": 1, "report": 1}, 0),
        ("Utilisation Module Full Access", "Donor",  {"read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1,
                                                      "cancel": 1, "import": 1, "export": 1, "share": 1, "email": 1, "report": 1}, 0),
        ("Utilisation Module Full Access", "Grant Agreement", "select_read", 0),
        ("Utilisation Module Full Access", "Budget Plan",  {"read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1,
                                                            "cancel": 1, "import": 1, "export": 1, "share": 1, "email": 1, "report": 1}, 0),
        ("Utilisation Module Full Access", "Budget Category",  {"read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1,
                                                                "cancel": 1, "import": 1, "export": 1, "share": 1, "email": 1, "report": 1}, 0),
        ("Utilisation Module Full Access", "Budget Sub-Category",  {"read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1,
                                                                    "cancel": 1, "import": 1, "export": 1, "share": 1, "email": 1, "report": 1}, 0),
        ("Utilisation Module Full Access", "Currency",  {"read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1,
                                                         "cancel": 1, "import": 1, "export": 1, "share": 1, "email": 1, "report": 1}, 0),
        ("Utilisation Module Full Access",
         "Engagement Checklist Master",  {"read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1,
                                          "cancel": 1, "import": 1, "export": 1, "share": 1, "email": 1, "report": 1}, 0),
    ]

    try:
        for role, doctype, permissions, permlevel in role_doctypes_permissions_level_mapping:
            add_permissions(role, doctype, permissions, permlevel)
    except Exception as e:
        frappe.log_error(f"Error setting up Utilisation roles: {e}")


def setup_org_toolkit_roles():
    """
    Sets up roles and permissions for the Document List module.
    """
    # format: (role, doctype, permissions, permission level)
    role_doctypes_permissions_level_mapping = [
        ("Fundraising Admin", "Document List", {
         "read": 1, "write": 1, "create": 1, "delete": 1}, 0),
    ]

    try:
        for role, doctype, permissions, permlevel in role_doctypes_permissions_level_mapping:
            add_permissions(role, doctype, permissions, permlevel)
    except Exception as e:
        frappe.log_error(f"Error setting up Document List roles: {e}")

def setup_fms_fundraising_admin_must_have_role():
    permissions_map = [
        ("Fundraising Admin", "Role", {"read": 1, "write": 1, "create": 1}),
        ("Fundraising Admin", "Role Profiles", {
            "read": 1, "write": 1, "create": 1, "delete": 1}),
        ("Fundraising Admin", "Custom DocPerm",
         {"read": 1, "write": 1, "create": 1}),
        ("Fundraising Admin", "User", {
            "read": 1, "write": 1, "create": 1, "delete": 1}),
        # permission level 1
        ("Fundraising Admin", "User", {"read": 1, "write": 1}, 1),
        ("Fundraising Admin", "User", {"select": 1}),
        ("Fundraising Admin", "LDAP Settings", {"read": 1,
                                                "write": 1, "create": 1, "delete": 1}),
        ("Fundraising Admin", "Currency", {
            "read": 1, "write": 1, "create": 1, "delete": 1}),
        ("Fundraising Admin", "Page", {"read": 1}),
        ("Fundraising Admin", "Module Profile", {"read": 1}),
        ("Fundraising Admin", "Data Import", {
            "read": 1, "write": 1, "create": 1, "delete": 1}),
        ("Fundraising Admin", "Data Export", {"read": 1, "write": 1}),
        ("Fundraising Admin", "Error Log", {"read": 1, "write": 1}),
        ("Fundraising Admin", "Dashboard List", {"read": 1}),
        ("Fundraising Admin", "Financial Year", {
            "read": 1, "write": 1, "create": 1, "delete": 1}),]

    try:
        for role, doctype, permissions, permlevel in permissions_map:
            add_permissions(role, doctype, permissions, permlevel)
    except Exception as e:
        frappe.log_error(f"Error setting up Fundraising Admin permissions: {e}")

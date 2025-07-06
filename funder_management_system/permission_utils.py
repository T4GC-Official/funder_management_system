import frappe
from .utils import create_roles_if_missing, add_permissions



def setup_modules_roles():
    """
    Sets up FMS-related roles and grants appropriate permissions.
    """
    fms_roles = ["Fundraising Manager",
                 "Fundraising Team Member",
                 "Programme Manager",
                 "Auditor"]
    
    create_roles_if_missing(fms_roles)
    setup_budget_allocation_module_roles()
    setup_donor_acquisition_module_roles()
    setup_donor_engagement_module_roles()
    setup_utilisation_module_roles()
    setup_org_toolkit_roles()



def setup_budget_allocation_module_roles():
   

    # format: (role, doctype, permissions, permission level)
    role_doctypes_permissions_level_mapping = [
        
        ("Fundraising Admin", "Budget Category", {"read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Budget Sub-Category", {"read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Financial Year", {"read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Currency", {"read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Budget Plan Template", {"read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Budget Plan", {"read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1, "report": 1}, 0),
        ("Fundraising Admin", "Budget Breakdown", {"read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Workspace", {"read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Custom HTML Block", {"read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),

        # ("Fundraising Manager", "Budget Category", {"read": 1}, 0),
        # ("Fundraising Manager", "Budget Sub-Category", {"read": 1}, 0),
        # ("Fundraising Manager", "Financial Year", {"read": 1}, 0),
        # ("Fundraising Manager", "Currency", {"read": 1}, 0),
        # ("Fundraising Manager", "Budget Plan Template", {"read": 1}, 0),
        # ("Fundraising Manager", "Budget Plan", {"read": 1, "report": 1}, 0),
        # ("Fundraising Manager", "Budget Breakdown", {"read": 1}, 0),
        # ("Fundraising Manager", "Workspace", {"read": 1}, 0),
        # ("Fundraising Manager", "Custom HTML Block", {"read": 1}, 0),

        # ("Fundraising Team Member", "Budget Category", {"read": 1}, 0),
        # ("Fundraising Team Member", "Budget Sub-Category", {"read": 1}, 0),
        # ("Fundraising Team Member", "Financial Year", {"read": 1}, 0),
        # ("Fundraising Team Member", "Currency", {"read": 1}, 0),
        # ("Fundraising Team Member", "Budget Plan Template", {"read": 1}, 0),
        # ("Fundraising Team Member", "Budget Plan", {"read": 1, "report": 1}, 0),
        # ("Fundraising Team Member", "Budget Breakdown", {"read": 1}, 0),
        # ("Fundraising Team Member", "Workspace", {"read": 1}, 0),
        # ("Fundraising Team Member", "Custom HTML Block", {"read": 1}, 0),
        # # @To DO: Review permission for the Programme Manager on Untilisation Module select @ajith 
        # ("Programme Manager", "Budget Category", {"read": 1}, 0),
        # ("Programme Manager", "Budget Sub-Category", {"read": 1}, 0),
        # ("Programme Manager", "Financial Year", {"read": 1}, 0),
        # ("Programme Manager", "Currency", {"read": 1}, 0),
        # ("Programme Manager", "Budget Plan Template", {"read": 1,}, 0),
        # ("Programme Manager", "Budget Plan", {"read": 1, "report": 1}, 0),
        # ("Programme Manager", "Budget Breakdown", {"read": 1}, 0),
        # ("Programme Manager", "Workspace", {"read": 1}, 0),
        # ("Programme Manager", "Custom HTML Block", {"read": 1}, 0),

        # ("Auditor", "Budget Category", {"read": 1}, 0),
        # ("Auditor", "Budget Sub-Category", {"read": 1}, 0),
        # ("Auditor", "Financial Year", {"read": 1}, 0),
        # ("Auditor", "Currency", {"read": 1}, 0),
        # ("Auditor", "Budget Plan Template", {"read": 1, "report": 1}, 0),
        # ("Auditor", "Budget Plan", {"read": 1, "report": 1}, 0),
        # ("Auditor", "Budget Breakdown", {"read": 1}, 0),
        # ("Auditor", "Workspace", {"read": 1}, 0),
        # ("Auditor", "Custom HTML Block", {"read": 1}, 0),
    ]

    try:
        for role, doctype, permissions, permlevel in role_doctypes_permissions_level_mapping:
            add_permissions(role, doctype, permissions, permlevel)
    except Exception as e:
        frappe.log_error(f"Error setting up FMS roles: {e}")

def setup_donor_acquisition_module_roles():
    
    # format: (role, doctype, permissions, permission level)
    role_doctypes_permissions_level_mapping = [
    
        ("Fundraising Admin", "Organisation Details", {"read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Organisation POC", {"read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Preferred Means of Communication", {"read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Organisation Lead", {"read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Compliance Checklist", {"read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Thematic Area", {"read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Source of Connection", {"read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Category", {"read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),



        # ("Fundraising Manager", "Organisation Details", {"read": 1,"write": 1, "create": 1, "delete": 1}, 0), 
        # ("Fundraising Manager", "Organisation POC", {"read": 1,"write": 1, "create": 1, "delete": 1}, 0), 
        # ("Fundraising Manager", "Preferred Means of Communication", {"read": 1,"write": 1, "create": 1, "delete": 1}, 0), 
        # ("Fundraising Manager", "Organisation Lead", {"read": 1,"write": 1, "create": 1, "delete": 1}, 0), 
        # ("Fundraising Manager", "Compliance Checklist", {"read": 1,"write": 1, "create": 1, "delete": 1}, 0), 
        # ("Fundraising Manager", "Thematic Area", {"read": 1,"write": 1, "create": 1, "delete": 1}, 0), 
        # ("Fundraising Manager", "Source of Connection", {"read": 1,"write": 1, "create": 1, "delete": 1}, 0), 
        # ("Fundraising Manager", "Category", {"read": 1,"write": 1, "create": 1, "delete": 1}, 0), 
    
        # ("Fundraising Team Member", "Organisation POC", {"read": 1,"write": 1, "create": 1, "delete": 1}, 0), 
        # ("Fundraising Team Member", "Organisation Details", {"read": 1,"write": 1, "create": 1, "delete": 1}, 0), 
        # ("Fundraising Team Member", "Preferred Means of Communication", {"read": 1,"write": 1, "create": 1, "delete": 1}, 0), 
        # ("Fundraising Team Member", "Organisation Lead", {"read": 1,"write": 1, "create": 1, "delete": 1}, 0), 
        # ("Fundraising Team Member", "Compliance Checklist", {"read": 1,"write": 1, "create": 1, "delete": 1}, 0), 
        # ("Fundraising Team Member", "Thematic Area", {"read": 1,"write": 1, "create": 1, "delete": 1}, 0), 
        # ("Fundraising Team Member", "Source of Connection", {"read": 1,"write": 1, "create": 1, "delete": 1}, 0), 
        # ("Fundraising Team Member", "Category", {"read": 1,"write": 1, "create": 1, "delete": 1}, 0), 

        # ("Programme Manager", "Organisation POC", {"read": 1}, 0),
        # ("Programme Manager", "Organisation Details", {"read": 1}, 0),
        # ("Programme Manager", "Preferred Means of Communication", {"read": 1}, 0),
        # ("Programme Manager", "Organisation Lead", {"read": 1}, 0),
        # ("Programme Manager", "Compliance Checklist", {"read": 1}, 0),
        # ("Programme Manager", "Thematic Area", {"read": 1}, 0),
        # ("Programme Manager", "Source of Connection", {"read": 1}, 0),
        # ("Programme Manager", "Category", {"read": 1}, 0),
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
        ("Fundraising Admin", "Engagement Checklist Master", {"read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Donor", {"read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Engagement Checklist", {"read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Tranche Details", {"read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
        ("Fundraising Admin", "Grant Agreement", {"read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),
       
        # ("Fundraising Manager", "Engagement Checklist Master", {"read": 1, "write": 1, "create": 1, "delete": 1}, 0),
        # ("Fundraising Manager", "Donor", {"read": 1, "write": 1, "create": 1, "delete": 1, "report": 1}, 0),
        # ("Fundraising Manager", "Engagement Checklist", {"read": 1, "write": 1, "create": 1, "delete": 1}, 0),
        # ("Fundraising Manager", "Tranche Details", {"read": 1, "write": 1, "create": 1, "delete": 1}, 0),
        # ("Fundraising Manager", "Grant Agreement", {"read": 1, "write": 1, "create": 1, "delete": 1}, 0),
       
        # ("Fundraising Team Member", "Engagement Checklist Master", {"read": 1, "write": 1, "create": 1, "delete": 1}, 0),
        # ("Fundraising Team Member", "Donor", {"read": 1, "write": 1, "create": 1, "delete": 1,  "report": 1}, 0),
        # ("Fundraising Team Member", "Engagement Checklist", {"read": 1, "write": 1, "create": 1, "delete": 1}, 0),
        # ("Fundraising Team Member", "Tranche Details", {"read": 1, "write": 1, "create": 1, "delete": 1}, 0),
        # ("Fundraising Team Member", "Grant Agreement", {"read": 1, "write": 1, "create": 1, "delete": 1}, 0),
       
        # ("Programme Manager", "Engagement Checklist Master", {"read": 1}, 0),
        # ("Programme Manager", "Donor", {"read": 1,  "report": 1}, 0),
        # ("Programme Manager", "Engagement Checklist", {"read": 1}, 0),
        # ("Programme Manager", "Tranche Details", {"read": 1}, 0),
        # ("Programme Manager", "Grant Agreement", {"read": 1}, 0),
       
        # ("Auditor", "Engagement Checklist Master", {"read": 1}, 0),
        # ("Auditor", "Donor", {"read": 1,  "report": 1}, 0),
        # ("Auditor", "Engagement Checklist", {"read": 1}, 0),
        # ("Auditor", "Tranche Details", {"read": 1}, 0),
        # ("Auditor", "Grant Agreement", {"read": 1}, 0),
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
        ("Fundraising Admin", "Expense Item", {"read": 1, "write": 1, "create": 1, "delete": 1, "report":1}, 0),
        ("Fundraising Admin", "Expense Item Child Table", {"read": 1, "write": 1, "create": 1, "delete": 1}, 0),
        ("Fundraising Admin", "Utilisation Record", {"read": 1, "write": 1, "create": 1, "delete": 1, "import": 1, "export": 1}, 0),

        # ("Fundraising Manager", "Expense Item", {"read": 1, "write": 1, "create": 1, "delete": 1, "report":1}, 0),
        # ("Fundraising Manager", "Expense Item Child Table", {"read": 1, "write": 1, "create": 1, "delete": 1}, 0),
        # ("Fundraising Manager", "Utilisation Record", {"read": 1, "write": 1, "create": 1, "delete": 1}, 0),
        
        # ("Fundraising Team Member", "Expense Item", {"read": 1, "write": 1, "create": 1, "delete": 1,  "report": 1}, 0),
        # ("Fundraising Team Member", "Expense Item Child Table", {"read": 1, "write": 1, "create": 1, "delete": 1}, 0),
        # ("Fundraising Team Member", "Utilisation Record", {"read": 1, "write": 1, "create": 1, "delete": 1}, 0),
        
        # ("Programme Manager", "Expense Item", {"read": 1, "write": 1, "create": 1, "delete": 1, "report": 1}, 0),
        # ("Programme Manager", "Expense Item Child Table", {"read": 1, "write": 1, "create": 1, "delete": 1}, 0),
        # ("Programme Manager", "Utilisation Record", {"read": 1, "write": 1, "create": 1, "delete": 1}, 0),
        
        # ("Auditor", "Expense Item", {"read": 1,  "report": 1}, 0),
        # ("Auditor", "Expense Item Child Table", {"read": 1}, 0),
        # ("Auditor", "Utilisation Record", {"read": 1}, 0),
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
        ("Fundraising Admin", "Document List", {"read": 1, "write": 1, "create": 1, "delete": 1}, 0),
        # ("Fundraising Manager", "Document List", {"read": 1, "write": 1, "create": 1, "delete": 1}, 0),
        # ("Fundraising Team Member", "Document List", {"read": 1}, 0),
        # ("Programme Manager", "Document List", {"read": 1}, 0),
        # ("Auditor", "Document List", {"read": 1}, 0),
    ]

    try:
        for role, doctype, permissions, permlevel in role_doctypes_permissions_level_mapping:
            add_permissions(role, doctype, permissions, permlevel)
    except Exception as e:
        frappe.log_error(f"Error setting up Document List roles: {e}")
        
def setup_dashboard_roles():
    pass
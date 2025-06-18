import frappe
from funder_management_system.api.dummy_data_api import (
    create_dummy_records,
    Budget_Allocation_Module,
    Donor_Acquisition_Module,
    Donor_Engagement_Module,
    create_test_users,
    insert_dummy_budget_category_and_sub_categories,
    create_dummy_budget_plan,
    create_organisation_records,
    generate_leads,
    change_lead_stage_and_create_donor,
    create_grant_agreement,
    add_dummy_utilisation_records
)

# Helper function for success logging
def log_success(message):
    """Log success messages to bench log"""
    logger = frappe.logger("dummy_data_api_success")
    logger.info(message)

@frappe.whitelist()
def create_all_dummy_records():
    """Create all dummy records - main entry point"""
    try:
        result = create_dummy_records()
        frappe.db.commit()
        log_success("All dummy records created successfully")
        return {"status": "success", "message": "All dummy records created successfully"}
    except Exception as e:
        frappe.log_error(f"Error in create_all_dummy_records: {str(e)}")
        return {"status": "error", "message": str(e)}

@frappe.whitelist()
def create_budget_allocation_data():
    """Create budget allocation module data"""
    try:
        Budget_Allocation_Module()
        frappe.db.commit()
        log_success("Budget allocation data created successfully")
        return {"status": "success", "message": "Budget allocation data created successfully"}
    except Exception as e:
        frappe.log_error(f"Error in Budget_Allocation_Module: {str(e)}")
        return {"status": "error", "message": str(e)}

@frappe.whitelist()
def create_donor_acquisition_data():
    """Create donor acquisition module data"""
    try:
        Donor_Acquisition_Module()
        frappe.db.commit()
        log_success("Donor acquisition data created successfully")
        return {"status": "success", "message": "Donor acquisition data created successfully"}
    except Exception as e:
        frappe.log_error(f"Error in Donor_Acquisition_Module: {str(e)}")
        return {"status": "error", "message": str(e)}

@frappe.whitelist()
def create_donor_engagement_data():
    """Create donor engagement module data"""
    try:
        Donor_Engagement_Module()
        frappe.db.commit()
        log_success("Donor engagement data created successfully")
        return {"status": "success", "message": "Donor engagement data created successfully"}
    except Exception as e:
        frappe.log_error(f"Error in Donor_Engagement_Module: {str(e)}")
        return {"status": "error", "message": str(e)}

@frappe.whitelist()
def create_test_users_api():
    """Create test users via API"""
    try:
        create_test_users()
        frappe.db.commit()
        log_success("Test users created successfully")
        return {"status": "success", "message": "Test users created successfully"}
    except Exception as e:
        frappe.log_error(f"Error in create_test_users: {str(e)}")
        return {"status": "error", "message": str(e)}

@frappe.whitelist()
def create_budget_categories():
    """Create budget categories and sub-categories"""
    try:
        insert_dummy_budget_category_and_sub_categories()
        frappe.db.commit()
        log_success("Budget categories created successfully")
        return {"status": "success", "message": "Budget categories created successfully"}
    except Exception as e:
        frappe.log_error(f"Error in insert_dummy_budget_category_and_sub_categories: {str(e)}")
        return {"status": "error", "message": str(e)}

@frappe.whitelist()
def create_organisations():
    """Create organisation records"""
    try:
        create_organisation_records()
        frappe.db.commit()
        log_success("Organisation records created successfully")
        return {"status": "success", "message": "Organisation records created successfully"}
    except Exception as e:
        frappe.log_error(f"Error in create_organisation_records: {str(e)}")
        return {"status": "error", "message": str(e)}

@frappe.whitelist()
def create_leads():
    """Generate leads from organisations"""
    try:
        generate_leads()
        frappe.db.commit()
        log_success("Leads generated successfully")
        return {"status": "success", "message": "Leads generated successfully"}
    except Exception as e:
        frappe.log_error(f"Error in generate_leads: {str(e)}")
        return {"status": "error", "message": str(e)}

@frappe.whitelist()
def create_utilisation_records():
    """Create utilisation records with parameters"""
    try:
        n_utilisation = int(frappe.form_dict.get('n_utilisation', 5))
        n_expense = int(frappe.form_dict.get('n_expense', 3))
        
        add_dummy_utilisation_records(n_utilisation, n_expense)
        frappe.db.commit()
        log_success(f"Created {n_utilisation} utilisation records with {n_expense} expenses each")
        return {
            "status": "success", 
            "message": f"Created {n_utilisation} utilisation records with {n_expense} expenses each"
        }
    except Exception as e:
        frappe.log_error(f"Error in add_dummy_utilisation_records: {str(e)}")
        return {"status": "error", "message": str(e)}

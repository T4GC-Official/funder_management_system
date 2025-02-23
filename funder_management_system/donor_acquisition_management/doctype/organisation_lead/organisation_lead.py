
import frappe # type: ignore
from frappe.model.document import Document # type: ignore
# Copyright (c) 2025, Tech4Good Community and contributors

class OrganisationLead(Document):
	pass


@frappe.whitelist()
def create_donor_from_lead(lead_name):
    logger = frappe.logger("organisation_lead")  # Make sure the logger is defined
    logger.info(f"Creating Donor Entry for Lead: {lead_name}")

    try:
        lead_doc = frappe.get_doc("Organisation Lead", lead_name)
        logger.info(f"Lead Document: {lead_doc}")
        doc = frappe.new_doc("Donor")
        doc.lead_name = lead_name
        doc.donor_name = lead_doc.lead_name
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        logger.info(f"Donor Entry Created for Lead: {lead_name}")
        return True
        

    except Exception as e:
        logger.error(f"Error creating donor: {str(e)}")
        frappe.log_error(f"Error creating donor: {str(e)}", "Donor Creation Error")
        return str(e)  # Failure


	
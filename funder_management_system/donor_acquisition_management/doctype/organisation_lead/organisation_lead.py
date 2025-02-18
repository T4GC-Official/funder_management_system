# Copyright (c) 2025, Tech4Good Community and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class OrganisationLead(Document):
	pass


@frappe.whitelist()
def create_donor_from_lead(lead_name):
    try:
        frappe.logger().info(f"Creating Donor Entry for Lead: {lead_name}")

        # Fetch the lead document
        lead_doc = frappe.get_doc("Organisation Lead", lead_name)

        # Create a new Donor document
        donor_doc = frappe.new_doc("Donor")
        donor_doc.lead_name = lead_doc.name  # Ensure correct field mapping
        donor_doc.organisation_name = lead_doc.organisation_name  # Add other necessary fields
        donor_doc.insert(ignore_permissions=True)

        frappe.db.commit()  # Commit changes to the database

        return True  # Success

    except Exception as e:
        frappe.log_error(title="Error Creating Donor", message=str(e))
        return False  # Failure

	
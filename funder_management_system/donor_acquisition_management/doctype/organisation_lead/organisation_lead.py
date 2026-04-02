import frappe  # type: ignore
from frappe.model.document import Document  # type: ignore

# Copyright (c) 2025, Tech4Good Community and contributors


class OrganisationLead(Document):
	pass
	# def validate(self):
	#     self.prevent_reverting_to_new()

	# def prevent_reverting_to_new(self):
	#     if self.lead_stage == "New Lead":
	#         stages = [entry.lead_stage for entry in self.table_lead_history]
	#         if "New Lead" in stages and any(stage != "New Lead" for stage in stages):
	#             frappe.throw("Cannot revert to 'New Lead' stage if the lead has already progressed to other stages.")


@frappe.whitelist()
def create_donor_from_lead(lead_name):
	logger = frappe.logger("organisation_lead")
	logger.info(f"Checking for existing Donor for Lead: {lead_name}")

	try:
		# Check if a Donor already exists for this lead
		existing_donor = frappe.get_all("Donor", filters={"lead_name": lead_name}, pluck="name")
		if existing_donor:
			return {"status": "duplicate", "message": f"Donor already exists: {existing_donor[0]}"}

		# Get Lead Document
		lead_doc = frappe.get_doc("Organisation Lead", lead_name)

		# Create New Donor
		doc = frappe.new_doc("Donor")
		doc.lead_name = lead_name
		doc.donor_name = lead_doc.lead_name

		# Copy assigned POCs if they exist
		if lead_doc.assigned_poc:
			for lead_poc in lead_doc.assigned_poc:
				row = doc.append("assigned_poc", {})
				row.organisation_poc_name = lead_poc.organisation_poc_name
				row.designation = lead_poc.designation
				row.phone = lead_poc.phone
				row.preferrend_means_of_communication = lead_poc.preferrend_means_of_communication
				row.internal_poc_name = lead_poc.internal_poc_name
				row.status = lead_poc.status
				row.email = lead_poc.email

		# Insert New Donor
		doc.insert(ignore_permissions=True)
		frappe.db.commit()

		logger.info(f"Donor Entry Created for Lead: {lead_name}")
		return {"status": "success", "message": f"Donor created from Lead: {lead_name}"}

	except Exception as e:
		logger.error(f"Error creating donor: {str(e)}")
		frappe.log_error(f"Error creating donor: {str(e)}", "Donor Creation Error")
		return {"status": "error", "message": str(e)}

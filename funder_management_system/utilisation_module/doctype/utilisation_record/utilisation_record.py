# Copyright (c) 2025, Tech4Good Community and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

frappe.utils.logger.set_log_level("DEBUG")  # Ensure debug logs are captured
logger = frappe.logger("utilisation_record", allow_site=True, file_count=50)
save_logger = frappe.logger("save_utilisation_record", allow_site=True, file_count=50)

class UtilisationRecord(Document):
    
	def validate(self):
		try:
			# Check if the utilisation record is in draft status
			if self.docstatus == 0:
				self.change_to_draft_status()
		except Exception as e:
			save_logger.error(f"Error in utilisation_record validate: {e}")
   
	def on_cancel(self):
		try:
			user = frappe.session.user
			logger.info(f"{user} requested to cancel utilisation record: {self.name}")

			# Fetch the Grant Disbursement Receipt
			grant_disbursement = frappe.get_doc("Grant Disbursement Receipt", self.gdr)
			logger.info(f"Grant Disbursement Receipt record fetched: {grant_disbursement.name}")	

			# Iterate through child table and update utilisation_record_created
			updated = False
			for row in grant_disbursement.utilisation_child_table:
				logger.info(f"Utilisation Child Table record fetched: {row.utilisation_record_created}")
				if (row.utilisation_record_created == "Submitted" or row.utilisation_record_created == "Amended" )and row.expenditure_record_name == self.name:
					row.utilisation_record_created = "Cancelled"
					updated = True
					logger.info(f"Utilisation Child Table record updated: {row.name}")
					break  # Stop once found

			# Save the parent document if any child record was updated
			if updated:
				grant_disbursement.save()
				frappe.db.commit()  # Ensure changes are committed
				logger.info(f"Grant Disbursement Receipt updated and saved: {grant_disbursement.name}")

			logger.info(f"{user}  Utilisation record successfully cancelled: {self.name}")	

		except Exception as e:
			logger.error(f"Error in utilisation_record on_cancel: {e}")

	def on_submit(self):
		try:
			user = frappe.session.user
			logger.info(f"{user} requested to submit utilisation record: {self.name}")
			# fetch amended from value and update the grant disbursement receipt child table link record
			grant_disbursement = frappe.get_doc("Grant Disbursement Receipt", self.gdr)
			logger.info(f"Grant Disbursement Receipt record amended from: {self.amended_from} to {self.name}")
			# Iterate through child table and update utilisation_record_created	
			for row in grant_disbursement.utilisation_child_table:
				logger.info(f"Utilisation Child Table record fetched: {row.utilisation_record_created}")
				if  row.expenditure_record_name == self.amended_from:
					row.utilisation_record_created = "Amended"
					row.expenditure_record_name = self.name
					break
			grant_disbursement.save()
			frappe.db.commit()  # Ensure changes are committed
			logger.info(f"Grant Disbursement Receipt updated and saved: {grant_disbursement.name}")
			
		except Exception as e:
			logger.error(f"Error in utilisation_record on_submit: {e}")


	def change_to_draft_status(self):
		try:
			user = frappe.session.user
			save_logger.info(f"{user} requested to change utilisation record to draft status: {self.name}")
			save_logger.info(f"the doc is amended from : {self.amended_from}")

			# Fetch the Grant Disbursement Receipt
			grant_disbursement = frappe.get_doc("Grant Disbursement Receipt", self.gdr)

			# Find the correct child table row
			row_to_update = None
			for row in grant_disbursement.utilisation_child_table:
				save_logger.info(f"Checking Utilisation Child Table record: {row.expenditure_record_name} and  self.amended_from: {self.amended_from}")
				if row.expenditure_record_name == self.amended_from:
					row_to_update = row
					break  # Stop loop when found

			# If a matching row is found, update it
			if row_to_update:
				row_to_update.utilisation_record_created = "Draft"
				row_to_update.expenditure_record_name = self.name
				save_logger.info(f"Updated Child Table Row: {row_to_update.name}")
				grant_disbursement.save()
				frappe.db.commit()
				save_logger.info(f"Grant Disbursement Receipt updated and saved: {self.name}")

			else:
				save_logger.warning(f"No matching record found for {self.amended_from} in child table.")

		except Exception as e:
			save_logger.error(f"Error in utilisation_record change_to_draft_status: {e}")

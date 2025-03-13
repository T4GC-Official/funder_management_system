# Copyright (c) 2025, Tech4Good Community and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

frappe.utils.logger.set_log_level("DEBUG")  # Ensure debug logs are captured
logger = frappe.logger("utilisation_record", allow_site=True, file_count=50)
logger_submit = frappe.logger("utilisation_record_submit", allow_site=True, file_count=50)

class UtilisationRecord(Document):
    
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
				if (row.utilisation_record_created == "Submitted" or row.utilisation_record_created == "Amended" or  row.utilisation_record_created == "Draft")and row.expenditure_record_name == self.name:
					row.utilisation_record_created = "Cancelled"
					updated = True
					logger.info(f"Utilisation Child Table record updated: {row.name}")
					break  # Stop once found

			# Save the parent document if any child record was updated
			if updated:
				grant_disbursement.child_table_value_updated = True
				grant_disbursement.save()
				frappe.db.commit()  # Ensure changes are committed
				logger.info(f"Grant Disbursement Receipt updated and saved: {grant_disbursement.name}")

			logger.info(f"Utilisation record successfully cancelled: {self.name}")	

		except Exception as e:
			logger.error(f"Error in utilisation_record on_cancel: {e}")

	def on_submit(self):
		try:
			user = frappe.session.user
			logger.info(f"{user} requested to submit utilisation record: {self.name}")
			grant_disbursement = frappe.get_doc("Grant Disbursement Receipt", self.gdr)
			logger.info(f"Grant Disbursement Receipt record amended from: {self.amended_from} to {self.name}")
			for row in grant_disbursement.utilisation_child_table:
				logger_submit.info(f"Request for Submit {self.name} and {row.expenditure_record_name}")
				logger.info(f"Utilisation Child Table record fetched: {row.utilisation_record_created}")
				if  row.expenditure_record_name == self.name:
					logger_submit.info(f"Request for Submit {self.amended_from} and {row.expenditure_record_name}")
					#update the utilised_amount and utilisation record created
					row.utilised_amount = self.utilised_amount	
					row.utilisation_record_created = "Amended"
					row.expenditure_record_name = self.name
					break
			grant_disbursement.child_table_value_updated = True
			grant_disbursement.save()
			frappe.db.commit()  # Ensure changes are committed
			logger.info(f"Grant Disbursement Receipt updated and saved: {grant_disbursement.name}")
			
		except Exception as e:
			logger.error(f"Error in utilisation_record on_submit: {e}")


	def update_draft_status(self,update_utilised_amount=False):
		try:
			user = frappe.session.user
			logger.info(f"{user} requested to change utilisation record to draft status: {self.name}")
			logger.info(f"the doc is amended from : {self.amended_from}")

			# Fetch the Grant Disbursement Receipt
			grant_disbursement = frappe.get_doc("Grant Disbursement Receipt", self.gdr)

			# Find the correct child table row
			row_to_update = None
			for row in grant_disbursement.utilisation_child_table:
				logger.info(f"Checking Utilisation Child Table record: {row.expenditure_record_name} and  self.amended_from: {self.amended_from}")
				if row.expenditure_record_name == self.amended_from:
					row_to_update = row
					break  # Stop loop when found

			# If a matching row is found, update it
			if row_to_update:
				row.utilised_amount = self.utilised_amount	
				row_to_update.utilisation_record_created = "Draft"
				row_to_update.expenditure_record_name = self.name
				logger.info(f"Updated Child Table Row: {row_to_update.name}")
				grant_disbursement.child_table_value_updated = True	
				grant_disbursement.save()
				frappe.db.commit()
				logger.info(f"Grant Disbursement Receipt updated and saved: {self.name}")

			else:
				if update_utilised_amount:
					row.utilised_amount = self.utilised_amount
					grant_disbursement.child_table_value_updated = True	
					grant_disbursement.save()
					frappe.db.commit()
					logger.info(f"Only the Utilised Amount is updated: {self.utilised_amount}")
				if not update_utilised_amount:
					logger.warning(f"No matching record found for {self.amended_from} in child table to update utilisation record as draft.")


		except Exception as e:
			logger.error(f"Error in utilisation_record change_to_draft_status: {e}")
	def on_change(self):
		try:
			self.update_draft_status(update_utilised_amount=True)
			logger.info(f" on save event triggered for utilisation record: {self.name}")

		except Exception as e:	
			logger.error(f"Error in utilisation_record on_save: {e}")
	def after_insert(self):
		try:
			self.update_draft_status()
			logger.info(f" after_insert event triggered for utilisation record: {self.name}")

		except Exception as e:	
			logger.error(f"Error in utilisation_record after_insert: {e}")

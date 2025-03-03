# Copyright (c) 2025, Tech4Good Community and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

frappe.utils.logger.set_log_level("DEBUG")  # Ensure debug logs are captured
logger = frappe.logger("utilisation_record", allow_site=True, file_count=50)

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
				if row.utilisation_record_created == 1 and row.expenditure_record_name == self.name:
					row.utilisation_record_created = 0
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

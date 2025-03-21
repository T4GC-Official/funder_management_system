# Copyright (c) 2025, Tech4Good Community and contributors
# For license information, please see license.txt

import time
import frappe # type: ignore
from frappe.model.document import Document # type: ignore
from funder_management_system.engagement_module.doctype.grant_agreement.grant_agreement import update_total_grant_amount_utilised


frappe.utils.logger.set_log_level("DEBUG")  # Ensure debug logs are captured
logger = frappe.logger("expense_item", allow_site=True, file_count=5)
logger_submit = frappe.logger("expense_item_submit", allow_site=True, file_count=5)
logger_update = frappe.logger("update_grant_agreement", allow_site=True, file_count=5)
logger_create = frappe.logger("create_utilisation_entries", allow_site=True, file_count=5)

class ExpenseItem(Document):
    
    
    
	def on_cancel(self):
		try:
			update_grant_expenditure(self.grant_agreement,self.grant_agreement_tranche, self.utilised_amount, increase=False)
			user = frappe.session.user
			logger.info(f"{user} requested to cancel utilisation record: {self.name}")

			# Fetch the Utilisation Record
			utilisation_record = frappe.get_doc("Utilisation Record", self.urn)
			logger.info(f"Utilisation Record record fetched: {utilisation_record.name}")	

			# Iterate through child table and update expense_item_created
			updated = False
			for row in utilisation_record.utilisation_child_table:
				logger.info(f"Utilisation Child Table record fetched: {row.utilisation_status}")
				if (row.utilisation_status == "Submitted" or row.utilisation_status == "Amended" or  row.utilisation_status == "Draft")and row.expenditure_record_name == self.name:
					row.utilisation_status = "Cancelled"
					updated = True
					logger.info(f"Utilisation Child Table record updated: {row.name}")
					break  # Stop once found

			# Save the parent document if any child record was updated
			if updated:
				utilisation_record.child_table_value_updated = True
				utilisation_record.save()
				frappe.db.commit()  # Ensure changes are committed
				logger.info(f"Utilisation Record updated and saved: {utilisation_record.name}")

			logger.info(f"Utilisation record successfully cancelled: {self.name}")	

		except Exception as e:
			logger.error(f"Error in expense_item on_cancel: {e}")

	def on_submit(self):
		try:
			update_grant_expenditure(self.grant_agreement,self.grant_agreement_tranche, self.utilised_amount,increase=True)
			user = frappe.session.user
			logger_submit.info(f"{user} requested to submit utilisation record: {self.name}")
			utilisation_record = frappe.get_doc("Utilisation Record", self.urn)
			logger_submit.info(f"Utilisation Record record amended from: {self.amended_from} to {self.name}")
			for row in utilisation_record.utilisation_child_table:
				logger_submit.info(f"Request for Submit {self.name} and {row.expenditure_record_name}")
				#logger_submit.info(f"Utilisation Child Table record fetched: {row.expense_item_created}")
				if  row.expenditure_record_name == self.name:
					logger_submit.info(f"Request for Submit {self.amended_from} and {row.expenditure_record_name}")
					logger_submit.info(f"Utilisation Child Table record status changed from: {row.utilisation_status} to 'Amended'")
					#update the utilised_amount and utilisation record created
					row.utilised_amount = self.utilised_amount	
					row.utilisation_status = "Amended"
					row.expenditure_record_name = self.name
					break
			utilisation_record.child_table_value_updated = True
			utilisation_record.save()
			frappe.db.commit()  # Ensure changes are committed
			logger_submit.info(f"Utilisation Record updated and saved: {utilisation_record.name}")
			
		except Exception as e:
			logger_submit.error(f"Error in expense_item on_submit: {e}")


	def update_draft_status(self,update_utilised_amount=False):
		try:
			user = frappe.session.user
			logger.info(f"{user} requested to change utilisation record to draft status: {self.name}")
			logger.info(f"the doc is amended from : {self.amended_from}")

			# Fetch the Utilisation Record
			grant_disbursement = frappe.get_doc("Utilisation Record", self.urn)

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
				row_to_update.utilisation_status = "Draft"
				row_to_update.expenditure_record_name = self.name
				logger.info(f"Updated Child Table Row: {row_to_update.name}")
				grant_disbursement.child_table_value_updated = True	
				grant_disbursement.save()
				frappe.db.commit()
				logger.info(f"Utilisation Record updated and saved: {self.name}")

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
			logger.error(f"Error in expense_item change_to_draft_status: {e}")
	def on_change(self):
		try:
			self.update_draft_status(update_utilised_amount=True)
			logger.info(f" on_change event triggered for utilisation record: {self.name}")

		except Exception as e:	
			logger.error(f"Error in expense_item on_save: {e}")
	def after_insert(self):
		try:
			self.update_draft_status()
			logger.info(f" after_insert event triggered for utilisation record: {self.name}")

		except Exception as e:	
			logger.error(f"Error in expense_item after_insert: {e}")

@frappe.whitelist()
def create_utilisation_entries(document_name):
    try:
        ur_doc = frappe.get_doc("Utilisation Record", document_name)
        frappe.enqueue(
        	"funder_management_system.utilisation_module.doctype.expense_item.expense_item.create_utilisation_entries_task",
            queue='long',
			job_name="Create Utilisation Entries",
            document_name=document_name,
            is_async=True
    	)
        
        frappe.msgprint(f"Job enqueued for creating the {len(ur_doc.utilisation_child_table)}Utilisation Entries", alert=True)
        logger_create.info(f"Enqueued create_utilisation_entries for document: {document_name}")
    except Exception as e:
        logger_create.error(f"Error enqueuing create_utilisation_entries: {e}")

    
    
def unlock_document(document_name):
    """Unlock the document and make it read-only"""
    try:
        logger_create.info(f"on_success | Unlocking and setting document {document_name} to read-only")
        # ur_doc = frappe.get_doc("Utilisation Record", document_name)
        # ur_doc.is_locked = 0  # Unlock the document
        # ur_doc.save(ignore_permissions=True)

        # # Make the document read-only
        # frappe.set_user_read_only("Utilisation Record", document_name, True)

    except Exception as e:
        logger_create.error(f"Error unlocking and setting document {document_name} to read-only: {e}")

def create_utilisation_entries_task(document_name): #we will convert this function to do bulk insert
    try:
        ur_doc = frappe.get_doc("Utilisation Record", document_name)
        count = 0
        utilisation_entries = []
        for row in ur_doc.utilisation_child_table:
            if row.utilisation_status == "New":
                utilisation_doc = frappe.get_doc({
                    "doctype": "Expense Item",
                    "donor": row.donor,
                    "grant_agreement": row.grant_agreement,
                    "category": row.category,
                    "expense_date": row.expense_date,
                    "expense_title": row.expense_title,
                    "grant_agreement_tranche": row.grant_agreement_tranche,
                    "sub_category": row.sub_category,
                    "utilised_amount": row.utilised_amount,
                    "quarters": row.quarters,
                    "budget_plan": row.budget_plan,
                    "financial_year": row.financial_year,
                    "urn": ur_doc.urn,
                    "docstatus": 1
                })
                utilisation_doc.insert(ignore_permissions=True)
                row.db_set("expenditure_record_name", utilisation_doc.name)
                row.db_set("utilisation_status", "Submitted")
                count += 1
                utilisation_entries.append(utilisation_doc.name)
                logger_create.info(f"{count}|Creating Utilisation Record: {row.expenditure_record_name} for {row.expense_title}")
                
                try:
                    logger_create(f"{count}| Updating grant expenditure in tranche for {utilisation_doc.name}")
                    update_grant_expenditure(row.grant_agreement, row.grant_agreement_tranche, row.utilised_amount)
                except Exception as update_error:
                    # Rollback the changes if update fails
                    utilisation_doc.cancel()
                    row.db_set("utilisation_status", "New")
                    logger.error(f"Failed to update grant expenditure for {utilisation_doc.name}: {str(update_error)}")
                    frappe.log_error(f"Failed to update grant expenditure for {utilisation_doc.name}: {str(update_error)}", "Expenditure Update Error")
                    return False

        if count > 0:
            ur_doc.child_table_value_updated = True
            ur_doc.save()
            frappe.db.commit()
            logger_create.info(f"Successfully created {count} utilisation records for {document_name}")
            if count == 1:
                frappe.msgprint(f"{count} Utilisation Entry Created", alert=True)
            else:
                frappe.msgprint(f"{count} Utilisation Entries Created", alert=True)

            return True

        else:
            logger.info(f"No new Expense Items Entries were created (Already Processed) for {document_name}")
            frappe.msgprint("No new Expense Items Entries were created (Already Processed)", alert=True)
            return None
    except Exception as e:
        logger.error(f"Error creating utilisation records: {str(e)}")
        frappe.log_error(f"Error creating utilisation records: {str(e)}", "Utilisation Creation Error")
        return False

def update_grant_expenditure(grant_agreement_name, grant_agreement_tranche, amount, increase=True):		
    try:
        logger_update.info(
            f"Request for update_grant_expenditure for Grant: {grant_agreement_name}, "
            f"Tranche: {grant_agreement_tranche}, Expense Amount: {amount}"
        )

        grant_agreement_doc = frappe.get_doc("Grant Agreement", grant_agreement_name)
        tranche_found = False  # Track if tranche exists

        for tranche in grant_agreement_doc.tranche_table:
            if tranche.tranche_name == grant_agreement_tranche:
                logger_update.info(f"Tranche '{grant_agreement_tranche}' found in Grant Agreement '{grant_agreement_name}'")
                tranche_found = True
                if increase:
                    tranche.total_tranche_expenditure += amount or 0
                    logger_update.info(f"Increase | Updated total expenditure for tranche '{grant_agreement_tranche}' to {tranche.total_tranche_expenditure}")
                    
                else:
                    tranche.total_tranche_expenditure = max(tranche.total_tranche_expenditure - (amount or 0), 0)
                    logger_update(f"Decrease | Updated total expenditure for tranche '{grant_agreement_tranche}' to {tranche.total_tranche_expenditure}")
                      # Prevent negative values

                break  # Stop iterating once found

        if not tranche_found:
            logger_update.warning(
                f"Tranche '{grant_agreement_tranche}' not found in Grant Agreement '{grant_agreement_name}'"
            )
            return  # Stop execution if tranche is missing

        #grant_agreement_doc.total_grant_amount_utilised, grant_agreement_doc.total_tranche_amount_utilised = update_total_grant_amount_utilised(grant_agreement_doc)
        #grant_agreement_doc.total_grant_amount_utilised = 
        update_total_grant_amount_utilised(grant_agreement_doc)
        logger_update.info(f"Total Grant Amount Utilised: {grant_agreement_doc.total_grant_amount_utilised} for {grant_agreement_doc.name}")
        grant_agreement_doc.save(ignore_permissions=True)
        frappe.db.commit()

    except Exception as e:
        logger_update.error(f"Error in update_grant_expenditure: {str(e)}", exc_info=True)
        


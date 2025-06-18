# Copyright (c) 2025, Tech4Good Community and contributors
# For license information, please see license.txt

import time
import frappe  # type: ignore
from frappe.model.document import Document  # type: ignore
from funder_management_system.engagement_module.doctype.grant_agreement.grant_agreement import update_total_grant_amount_utilised


frappe.utils.logger.set_log_level("DEBUG")  # Ensure debug logs are captured
logger = frappe.logger("expense_item", allow_site=True, file_count=5)
logger_submit = frappe.logger(
    "expense_item_submit", allow_site=True, file_count=5)
logger_update = frappe.logger(
    "update_grant_agreement", allow_site=True, file_count=5)
logger_create = frappe.logger(
    "create_utilisation_entries", allow_site=True, file_count=5)
loger_update_total = frappe.logger(
    "total_grant_amount", allow_site=True, file_count=5)

class ExpenseItem(Document):
    def on_cancel(self):
        try:
            update_grant_expenditure(
                self.grant_agreement, self.grant_agreement_tranche, self.utilised_amount, increase=False)
            user = frappe.session.user
            logger.info(
                f"{user} requested to cancel utilisation record: {self.name}")

            # Fetch the Utilisation Record
            utilisation_record = frappe.get_doc("Utilisation Record", self.urn)
            logger.info(
                f"Utilisation Record record fetched: {utilisation_record.name}")

            # Iterate through child table and update expense_item_created
            updated = False
            for row in utilisation_record.utilisation_child_table:
                logger.info(
                    f"Utilisation Child Table record fetched: {row.utilisation_status}")
                if (row.utilisation_status == "Submitted" or row.utilisation_status == "Amended" or row.utilisation_status == "Draft") and row.expenditure_record_name == self.name:
                    row.utilisation_status = "Cancelled"
                    updated = True
                    logger.info(
                        f"Utilisation Child Table record updated: {row.name}")
                    break  # Stop once found

            # Save the parent document if any child record was updated
            if updated:
                utilisation_record.child_table_value_updated = True
                utilisation_record.save()
                frappe.db.commit()  # Ensure changes are committed
                logger.info(
                    f"Utilisation Record updated and saved: {utilisation_record.name}")

            logger.info(
                f"Utilisation record successfully cancelled: {self.name}")

            update_grand_total_in_utilisation_record(self.urn)
        except Exception as e:
            logger.error(f"Error in expense_item on_cancel: {e}")

    def update_draft_status(self, update_utilised_amount=False):
        try:
            user = frappe.session.user
            logger.info(
                f"{user} requested to change utilisation record to draft status: {self.name}")
            logger.info(f"the doc is amended from : {self.amended_from}")

            # Fetch the Utilisation Record
            grant_disbursement = frappe.get_doc("Utilisation Record", self.urn)

            # Find the correct child table row
            row_to_update = None
            for row in grant_disbursement.utilisation_child_table:
                logger.info(
                    f"Checking Utilisation Child Table record: {row.expenditure_record_name} and  self.amended_from: {self.amended_from}")
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
                logger.info(
                    f"Utilisation Record updated and saved: {self.name}")

            else:
                if update_utilised_amount:
                    row.utilised_amount = self.utilised_amount
                    grant_disbursement.child_table_value_updated = True
                    grant_disbursement.save()
                    frappe.db.commit()
                    logger.info(
                        f"Only the Utilised Amount is updated: {self.utilised_amount}")
                if not update_utilised_amount:
                    logger.warning(
                        f"No matching record found for {self.amended_from} in child table to update utilisation record as draft.")

        except Exception as e:
            logger.error(f"Error in expense_item change_to_draft_status: {e}")

    def on_change(self):
        try:
            self.update_draft_status(update_utilised_amount=True)
            logger.info(
                f" on_change event triggered for utilisation record: {self.name}")

        except Exception as e:
            logger.error(f"Error in expense_item on_save: {e}")

    def after_insert(self):
        try:
            self.update_draft_status()
            logger.info(
                f" after_insert event triggered for utilisation record: {self.name}")

        except Exception as e:
            logger.error(f"Error in expense_item after_insert: {e}")


@frappe.whitelist()
def create_utilisation_entries_job(document_name):
    try:
        ur_doc = frappe.get_doc("Utilisation Record", document_name)
        frappe.enqueue(
            "funder_management_system.utilisation_module.doctype.expense_item.expense_item.create_utilisation_entries_task",
            queue='long',
            job_name="Create Utilisation Entries",
            document_name=document_name,
            is_async=True
        )
        # Todo: function to lock the Utilisation Record and then
        # keep checking the job status and it the job is completed return true
        frappe.msgprint(
            f"Job Enqueued for creating the {len(ur_doc.utilisation_child_table)} Expense Items for Utilisation Record: {document_name}", alert=True)
        logger_create.info(
            f"Job Enqueued for creating the {len(ur_doc.utilisation_child_table)} Expense Items for Utilisation Record: {document_name}")
    except Exception as e:
        logger_create.error(f"Error enqueuing create_utilisation_entries: {e}")


@frappe.whitelist()
# we will convert this function to do bulk insert
def create_utilisation_entries(document_name):
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
                logger_create.info(
                    f"{count}|Creating Utilisation Record: {row.expenditure_record_name} for {row.expense_title}")

        if count > 0:
            logger_create.info(
                f"utilisation entries in Expense Items: {utilisation_entries}")
            update_grant_expenditure_new(utilisation_entries)

            update_grand_total_in_utilisation_record(document_name)
            
            ur_doc.child_table_value_updated = True
            # ur_doc.save() this will cause the error because the document is already saved
            frappe.db.commit()
            logger_create.info(
                f"Successfully created {count} utilisation records for {document_name}")
            if count == 1:
                frappe.msgprint(
                    f"{count} Utilisation Entry Created", alert=True)
            else:
                frappe.msgprint(
                    f"{count} Utilisation Entries Created", alert=True)

            return {"status": True, "message": f"Successfully created {count} utilisation records for {document_name}"}

        else:
            logger_create.info(
                f"No new Expense Items Entries were created (Already Processed) for {document_name}")
            frappe.msgprint(
                "No new Expense Items Entries were created (Already Processed)", alert=True)
            return None
    except Exception as e:
        logger.error(f"Error creating utilisation records: {str(e)}")
        frappe.log_error(
            f"Error creating utilisation records: {str(e)}", "Utilisation Creation Error")
        return False


def update_grant_expenditure_new(utilisation_entries):
    for utilisation_entry in utilisation_entries:
        logger_create.info(
            f"Updating grant expenditure for {utilisation_entry}")
        utilisation_doc = frappe.get_doc("Expense Item", utilisation_entry)
        try:
            update_grant_expenditure(utilisation_doc.grant_agreement,
                                     utilisation_doc.grant_agreement_tranche, utilisation_doc.utilised_amount)
        except:
            logger_create.error(
                f"Error updating grant expenditure for {utilisation_entry}")
            return False


def update_grant_expenditure(grant_agreement_name, grant_agreement_tranche, amount, increase=True):
    try:
        grant_agreement_doc = frappe.get_doc(
            "Grant Agreement", grant_agreement_name)
        tranche_found = False  # Track if tranche exists
        logger_create.info(
            f"Total Tranche:{len(grant_agreement_doc.tranche_table)}")
        for tranche in grant_agreement_doc.tranche_table:
            if tranche.tranche_name == grant_agreement_tranche:
                tranche_found = True
                if increase:
                    tranche.total_tranche_expenditure += amount or 0
                    logger_create.info(
                        f"Increase | Updated total expenditure for tranche '{grant_agreement_tranche}' to {tranche.total_tranche_expenditure}")
                else:
                    tranche.total_tranche_expenditure = max(
                        tranche.total_tranche_expenditure - (amount or 0), 0)
                    logger_create.info(
                        f"Decrease | Updated total expenditure for tranche '{grant_agreement_tranche}' to {tranche.total_tranche_expenditure}")
                    # Prevent negative values

                break  # Stop iterating once found

        if not tranche_found:
            logger_create.warning(
                f"Tranche '{grant_agreement_tranche}' not found in Grant Agreement '{grant_agreement_name}'"
            )
            return
        update_total_grant_amount_utilised(grant_agreement_doc)
        grant_agreement_doc.save(ignore_permissions=True)
        frappe.db.commit()

    except Exception as e:
        logger_update.error(
            f"Error in update_grant_expenditure: {str(e)}", exc_info=True)


def update_grand_total_in_utilisation_record(urn):
    try:
        utilisation_record = frappe.get_doc("Utilisation Record", urn)

        grand_total_result = frappe.db.sql("""
            SELECT SUM(utilised_amount) 
            FROM `tabExpense Item`
            WHERE urn = %s AND docstatus = 1
        """, (urn,), as_list=True)

        grand_total = grand_total_result[0][0] or 0.0 if grand_total_result else 0.0

        frappe.db.set_value("Utilisation Record", urn, "grand_total", grand_total)
        loger_update_total.info(f"Grand total updated for Utilisation Record {urn}: {grand_total}")
    except Exception as e:
        loger_update_total.error(f"Error updating grand total for Utilisation Record {urn}: {e}")
        frappe.log_error(frappe.get_traceback(), f"Grand Total Update Failed for URN: {urn}")



@frappe.whitelist()
def submit_record(document_name):
    try:
        document = frappe.get_doc("Expense Item", document_name)
        if not document:
            frappe.throw(f"Expense Item not found",
                         exc=frappe.DoesNotExistError)
        update_grant_expenditure(
            document.grant_agreement, document.grant_agreement_tranche, document.utilised_amount, increase=True)
        user = frappe.session.user
        logger_submit.info(
            f"{user} requested to submit utilisation record: {document.name}")
        utilisation_record = frappe.get_doc("Utilisation Record", document.urn)
        logger_submit.info(
            f"Utilisation Record record amended from: {document.amended_from} to {document.name}")
        for row in utilisation_record.utilisation_child_table:
            if row.expenditure_record_name == document.name:
                row.utilised_amount = document.utilised_amount
                row.utilisation_status = "Amended"
                row.expenditure_record_name = document.name
                break
        utilisation_record.child_table_value_updated = True
        utilisation_record.save()
        update_grand_total_in_utilisation_record(utilisation_record.urn)
        logger_submit.info(
            f"Utilisation Record {utilisation_record.name} updated with new expenditure record: {document.name}")
        frappe.db.commit()
        logger_submit.info(
            f"Utilisation Record {utilisation_record.name} updated and saved")
        
        

    except Exception as e:
        logger_submit.error(
            f"Error in submitting Expense Item Record: {document_name}: {e}")


@frappe.whitelist()
def create_bulk_utilisation_entries(document_name):
    try:
        utilisation_record_doc = frappe.get_doc(
            "Utilisation Record", document_name)
        utilisation_entries = []
        child_updates = []
        grant_updates = []

        for row in utilisation_record_doc.utilisation_child_table:
            if row.utilisation_status == "New":
                utilisation_entries.append([
                    row.donor,
                    row.grant_agreement,
                    row.category,
                    row.expense_date,
                    row.expense_title,
                    row.grant_agreement_tranche,
                    row.sub_category,
                    row.utilised_amount,
                    row.quarters,
                    row.budget_plan,
                    row.financial_year,
                    utilisation_record_doc.urn,
                    1  # docstatus
                ])
                child_updates.append(row)
                grant_updates.append(
                    (row.grant_agreement, row.grant_agreement_tranche, row.utilised_amount))

        if utilisation_entries:
            # Using `bulk_insert` for fast batch insertion
            frappe.db.bulk_insert(
                "Expense Item",
                fields=[
                    "donor", "grant_agreement", "category", "expense_date", "expense_title",
                    "grant_agreement_tranche", "sub_category", "utilised_amount", "quarters",
                    "budget_plan", "financial_year", "urn", "docstatus"
                ],
                values=utilisation_entries
            )

            # Fetch inserted document names
            inserted_docs = frappe.db.get_list(
                "Expense Item",
                # Assuming `urn` is unique for this batch
                filters={"urn": utilisation_record_doc.urn},
                fields=["name"]
            )

            if len(inserted_docs) != len(child_updates):
                frappe.log_error("Mismatch in inserted records",
                                 "Utilisation Entry Error")
                return False

            # Update child table records
            for row, inserted_doc in zip(child_updates, inserted_docs):
                row.db_set("expenditure_record_name", inserted_doc["name"])
                row.db_set("utilisation_status", "Submitted")

            utilisation_record_doc.child_table_value_updated = True
            utilisation_record_doc.save()
            frappe.db.commit()

            # Enqueue bulk update for grant expenditures
            frappe.enqueue(update_grant_expenditure, grants=grant_updates,
                           queue='long', job_name="Update Grant Expenditure")

            frappe.msgprint(
                f"{len(utilisation_entries)} Expense Items Created", alert=True)
            return True
        else:
            frappe.msgprint(
                "No new Expense Items Entries were created (Already Processed)", alert=True)
            return None
    except Exception as e:
        frappe.log_error(
            f"Error creating utilisation records: {str(e)}", "Utilisation Creation Error")
        return False

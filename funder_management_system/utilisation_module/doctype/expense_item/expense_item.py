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

    def childTableUpdated(self):
        try:
            user = frappe.session.user
            logger.info(
                f"{user} requested to change utilisation record to draft status: {self.name}")
            utilisation_record = frappe.get_doc("Utilisation Record", self.urn)
            utilisation_record.child_table_value_updated = True
            utilisation_record.save()
            frappe.db.commit()
            logger.info(
                    f"Utilisation Record updated and saved: {self.name}")
        except Exception as e:
            logger.error(f"Error in expense_item change_to_draft_status: {e}")

    def on_change(self):
        try:
            self.childTableUpdated(self)
            logger.info(
                f" on_change event triggered for utilisation record: {self.name}")

        except Exception as e:
            logger.error(f"Error in expense_item on_save: {e}")

    def after_insert(self):
        try:
            self.childTableUpdated(self)
            logger.info(
                f" after_insert event triggered for utilisation record: {self.name}")

        except Exception as e:
            logger.error(f"Error in expense_item after_insert: {e}")

    def on_trash(self):
        try:
            user = frappe.session.user
            logger.info(
                f"{user} requested to delete to delete expense item record: {self.name}")
            utilisation_record = frappe.get_doc("Utilisation Record", self.urn)
            for row in utilisation_record.utilisation_child_table:
                if row.expenditure_record_name == self.name:
                    utilisation_record.utilisation_child_table.remove(row)
                    utilisation_record.save()
                    frappe.db.commit()
                    logger.debug(
                        f"Expense item {self.name} removed from Utilisation Record {utilisation_record.name}")

            reload_utilisation_record(self.name)

            update_grand_total_in_utilisation_record(self.urn)
        except Exception as e:
            logger.error(f"Error in expense_item on_trash: {e}")



@frappe.whitelist()

def create_utilisation_entries(document_name):
    try:
        ur_doc = frappe.get_doc("Utilisation Record", document_name)
        count = 0
        utilisation_entries = []
        for row in ur_doc.utilisation_child_table:
            if row.utilisation_status == "New":
                expense_item_doc = frappe.new_doc("Expense Item")
                expense_item_doc.donor = row.donor
                expense_item_doc.grant_agreement = row.grant_agreement
                expense_item_doc.category = row.category
                expense_item_doc.expense_date = row.expense_date
                expense_item_doc.expense_title = row.expense_title
                expense_item_doc.grant_agreement_tranche = row.grant_agreement_tranche
                expense_item_doc.sub_category = row.sub_category
                expense_item_doc.utilised_amount = row.utilised_amount
                expense_item_doc.quarters = row.quarters
                expense_item_doc.budget_plan = row.budget_plan
                expense_item_doc.financial_year = row.financial_year
                expense_item_doc.urn = ur_doc.urn
                expense_item_doc.insert(ignore_permissions=True)
                expense_item_doc.submit()
                row.db_set("expenditure_record_name", expense_item_doc.name)
                row.db_set("utilisation_status", "Submitted")
                count += 1
                utilisation_entries.append(expense_item_doc.name)

        logger_create.info(
            f"{count}|Creating Utilisation Record: {expense_item_doc.name} for {row.expense_title}"
        )

        if count > 0:
            logger_create.info(
                f"utilisation entries in Expense Items: {utilisation_entries}")
            update_expenditure_for_utilisation_entries(utilisation_entries)
            update_grand_total_in_utilisation_record(document_name)
            ur_doc.child_table_value_updated = True
            frappe.db.commit()
            reload_utilisation_record(document_name)
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
            return {"status": False, "message": "No new Expense Items Entries were created (Already Processed)"}
    except Exception as e:
        logger.error(f"Error creating utilisation records: {str(e)}")
        frappe.log_error(
            f"Error creating utilisation records: {str(e)}", "Utilisation Creation Error")
        return False


def update_expenditure_for_utilisation_entries(utilisation_entries):
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

        frappe.db.set_value("Utilisation Record", urn,
                            "grand_total", grand_total)
        loger_update_total.info(
            f"Grand total updated for Utilisation Record {urn}: {grand_total}")
    except Exception as e:
        loger_update_total.error(
            f"Error updating grand total for Utilisation Record {urn}: {e}")
        frappe.log_error(frappe.get_traceback(),
                         f"Grand Total Update Failed for URN: {urn}")


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


def reload_utilisation_record(document_name):
    frappe.publish_realtime(
                event="reload_utilisation",
                message={"utilisation": document_name},
                user=None  # or None for all users
            )
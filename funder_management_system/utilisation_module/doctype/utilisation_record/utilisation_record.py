import frappe # type: ignore
from frappe.model.document import Document # type: ignore

frappe.utils.logger.set_log_level("DEBUG")  # Ensure debug logs are captured
logger = frappe.logger("utilisation_record", allow_site=True, file_count=50)

class UtilisationRecord(Document):
    pass


@frappe.whitelist()
def create_utilisation_entries(document_name):
    try:
        user = frappe.session.user
        logger.info(f"{user} requested to create expenditure records for Utilisation Record: {document_name}")

        ur_doc = frappe.get_doc("Utilisation Record", document_name)
        count = 0
        utilisation_entries = []

        logger.info(f"Creating utilisation records for Utilisation Record: {document_name}")

        for row in ur_doc.utilisation_child_table:
            if row.utilisation_status=="Submitted":
                logger.info(f"Skipping Utilisation Record creation for {row.name} as it was already submitted")
                continue
            if row.utilisation_status == "Cancelled":
                logger.info(f"Skipping Utilisation Record creation for {row.name} as it was cancelled")
                continue
            if row.utilisation_status == "Amended":
                logger.info(f"Skipping Utilisation Record creation for {row.name} as it was Amended")
                continue
            if row.utilisation_status == "Draft":
                logger.info(f"Skipping Utilisation Record creation for {row.name} as it was Draft")
                continue

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
                "docstatus":1
            })

            utilisation_doc.insert(ignore_permissions=True)
            # Update the child table row
            row.db_set("expenditure_record_name", utilisation_doc.name)
            row.db_set("utilisation_status", "Submitted")

            count += 1
            utilisation_entries.append(utilisation_doc.name)

            logger.info(f"Created Utilisation Record: {utilisation_doc.name} for Grant Agreement {ur_doc.grant_agreement}")

        if count > 0:
            frappe.db.commit()
            logger.info(f"Successfully created {count} utilisation records for {document_name}")
            if count == 1:
                frappe.msgprint(f"{count} Utilisation Entry Created", alert=True)
            else:
                frappe.msgprint(f"{count} Utilisation Entries Created", alert=True)
            return utilisation_entries
        else:
            logger.info(f"No new Expense Items Entries were created (Already Processed) for {document_name}")
            frappe.msgprint("No new  Expense Items Entries were created (Already Processed)", alert=True)
            return None
    except Exception as e:
        logger.error(f"Error creating utilisation records: {str(e)}")
        frappe.log_error(f"Error creating utilisation records: {str(e)}", "Utilisation Creation Error")
        return False


@frappe.whitelist()
def check_if_child_table_is_updated(document_name):
    try:
        # Fetch the Utilisation Record
        urn_doc = frappe.get_doc("Utilisation Record", document_name)
        if urn_doc.child_table_value_updated:
            logger.info(f"Utilisation Record child table is updated: {urn_doc.name}")
            # Update the child table value to false and save
            urn_doc.child_table_value_updated = False
            urn_doc.save()
            frappe.db.commit()
            return True
        else:
            return False
    except Exception as e:
        logger.error(f"Error in check_if_child_table_is_updated: {e}")
        return False

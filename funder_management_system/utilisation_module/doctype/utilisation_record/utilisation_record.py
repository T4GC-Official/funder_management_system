import frappe # type: ignore
from frappe.model.document import Document # type: ignore

frappe.utils.logger.set_log_level("DEBUG")  # Ensure debug logs are captured
logger = frappe.logger("utilisation_record", allow_site=True, file_count=50)

class UtilisationRecord(Document):
    pass


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

@frappe.whitelist()
def count_expense_items(urn):
    # Count both Submitted and Cancelled records in one query
    counts = {
        1: frappe.db.count('Expense Item', filters={'urn': urn, 'docstatus': 1}),  # Submitted
        2: frappe.db.count('Expense Item', filters={'urn': urn, 'docstatus': 2})   # Cancelled
    }
    return counts
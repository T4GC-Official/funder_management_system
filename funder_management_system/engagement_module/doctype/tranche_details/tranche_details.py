# Copyright (c) 2025, Tech4Good Community and contributors
# For license information, please see license.txt

from frappe.model.document import Document # type: ignore
import frappe # type: ignore
from frappe.utils import add_days, today, getdate # type: ignore

class TrancheDetails(Document):
	pass

def check_tranche_due_date_and_change_tranche_status():
    """Check due dates in tranche_table and update status if overdue."""

    tranche_details = frappe.get_all("Tranche Details",
                                     fields=["name", "parent", "due_date", "tranche_status"],
                                     filters={"parenttype": "Grant Agreement", "tranche_status": "Pending - On Time"})

    for tranche in tranche_details:
        if getdate(today()) > getdate(tranche.due_date):
            # Update the tranche status to "Pending - Delayed"
            frappe.db.set_value("Tranche Details", tranche.name, "tranche_status", "Pending - Delayed")

    frappe.db.commit()  # Commit after the loop to optimize performance
    frappe.logger().info("Tranche status update completed.")


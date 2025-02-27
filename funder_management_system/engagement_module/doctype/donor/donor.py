# Copyright (c) 2025, Tech4Good Community and contributors
# For license information, please see license.txt

from frappe.model.document import Document # type: ignore
import frappe # type: ignore
from frappe.utils import add_days, today, getdate # type: ignore

class Donor(Document):
    pass

def send_engagement_checklist_item_reminders():
    """Send reminders for engagement checklist items due today and update next reminder dates."""
    today_date = getdate(today())

    query = """
        SELECT d.name AS donor_name, d.owner, e.name AS item_name, e.item, e.next_reminder_date, e.item_frequency
        FROM `tabDonor` d
        JOIN `tabEngagement Checklist` e ON e.parent = d.name
        WHERE e.next_reminder_date = %s
    """

    due_items = frappe.db.sql(query, (today_date,), as_dict=True)

    # Process due items
    for item in due_items:
        next_reminder_date = calculate_next_reminder_date(item["next_reminder_date"], item["item_frequency"])

        # Create system notification
        create_system_notification(item["owner"], item["item"], item["donor_name"])

        # Update the next reminder date in the child table (Batch Update)
        frappe.db.set_value("Engagement Checklist", item["item_name"], "next_reminder_date", next_reminder_date)

    frappe.db.commit()  # Commit once to improve performance


def create_system_notification(recipient, item, donor_name):
    """Create a system notification for the recipient."""
    notification = frappe.get_doc({
        "doctype": "Notification Log",
        "subject": f"Reminder: {item} for Donor {donor_name}",
        "email_content": f"Reminder: It's time for {item}. Please take necessary action.",
        "for_user": recipient,
        "type": "Alert",
        "document_type": "Donor",
        "document_name": donor_name,
    })
    notification.insert(ignore_permissions=True)
    frappe.db.commit()  # Ensure the notification is committed to the database

def calculate_next_reminder_date(current_date, frequency):
    """Calculate the next reminder date based on the frequency."""

    if not current_date:
        # Default to today's date if current_date is missing
        current_date = getdate(today())

    if isinstance(current_date, str):
        # Convert string date to datetime.date object
        current_date = getdate(current_date)

    frequency_mapping = {
        "Monthly": 30,
        "Quarterly": 90,
        "Half Yearly": 180,
        "Yearly": 365,
    }

    next_reminder_date = add_days(current_date, frequency_mapping.get(frequency, 1))

    frappe.logger().info(f"Calculated next_reminder_date: {next_reminder_date} for frequency: {frequency} (Current Date: {current_date})")

    return next_reminder_date # Default to +1 day

# Copyright (c) 2025, Tech4Good Community and contributors
# For license information, please see license.txt

from frappe.model.document import Document # type: ignore
import frappe # type: ignore
from frappe.utils import add_days, today, getdate # type: ignore

class Donor(Document):
    pass

def send_engagement_checklist_item_reminders():
    today_date = getdate(today())

    # Fetch all Donors where at least one checklist item has today's reminder date
    donors = frappe.get_all("Donor", fields=["name", "owner"])

    for donor in donors:
        donor_doc = frappe.get_doc("Donor", donor.name)

        for item in donor_doc.get("engagement_checklist_table", []):
            if item.next_reminder_date == today_date:
                # Ensure next_reminder_date is always set
                next_reminder_date = calculate_next_reminder_date(item.next_reminder_date, item.item_frequency)

                # Create System Notification
                create_system_notification(donor_doc.owner, item.item, donor_doc.name)

                # Update the next reminder date in the child table
                frappe.db.set_value(
                    "Engagement Checklist", item.name, "next_reminder_date", next_reminder_date
                )

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

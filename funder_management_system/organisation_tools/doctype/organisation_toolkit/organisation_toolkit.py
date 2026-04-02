# Copyright (c) 2025, Tech4Good Community and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_days, getdate, today


class OrganisationToolkit(Document):
	pass


def send_reminder_for_documents():
	"""Send reminders for documents that are due for renewal."""
	today_date = getdate(today())
	document_list = frappe.get_all("Document List", fields=["name", "owner"])

	for document in document_list:
		document_doc = frappe.get_doc("Document List", document.name)

		for doc in document_doc.get("organisation_docs", []):
			if doc.notification_trigger_date == today_date:
				create_system_notification(document_doc.owner, document_doc.list_name, doc.document_name)


def create_system_notification(recipient, list_name, document_name):
	"""Create a system notification for the recipient."""
	notification = frappe.get_doc(
		{
			"doctype": "Notification Log",
			"subject": f"Reminder: {document_name} in {list_name} is due for renewal today",
			"email_content": f"Reminder: {document_name} in {list_name} is due for renewal today",
			"for_user": recipient,
			"type": "Alert",
			"document_type": "Document List",
			"document_name": list_name,
		}
	)
	notification.insert(ignore_permissions=True)
	frappe.db.commit()  # Ensure the notification is committed to the database
	frappe.publish_realtime(
		"notification", {"type": "Alert", "message": notification.subject}, user=recipient
	)

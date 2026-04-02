import frappe


def get_permission_query_conditions(user):
	if not user:
		user = frappe.session.user

	if user == "Administrator":
		return None  # No filtering

	return """`tabReport`.name IN (
            'Budget vs Utilisation Report',
            'Donation vs Utilisation Report',
            'Budget Plan Report','ToDo'
        )"""


def has_permission(doc, ptype, user):

	if user == "Administrator":
		return True

	return doc.name in [
		"Budget vs Utilisation Report",
		"Donation vs Utilisation Report",
		"Budget Plan ReportToDo",
	]

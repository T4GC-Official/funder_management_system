import frappe


def get_permission_query_conditions(user):
	if not user:
		user = frappe.session.user

	if user == "Administrator":
		return None

	allowed_pages = [
		"fundraising-dashboard",
		"donor-acquisition-ma",
		"cashflow-dashboard",
		"user-profile",
	]
	escaped = "', '".join(allowed_pages)
	return f"`tabPage`.name IN ('{escaped}')"


def has_permission(doc, ptype, user):
	if user == "Administrator":
		return True

	return doc.name in [
		"fundraising-dashboard",
		"donor-acquisition-ma",
		"cashflow-dashboard",
		"user-profile",
	]

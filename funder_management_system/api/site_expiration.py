import logging

import frappe
from frappe.utils import getdate, nowdate

log = logging.getLogger(__name__)


def check_and_handle_expiration():
	"""Check if site has expired and handle expiration logic."""
	try:
		expiration_date_str = frappe.local.conf.get("site_expiration_date")
		if not expiration_date_str:
			return False

		try:
			expiration_date = getdate(expiration_date_str)
		except (ValueError, TypeError) as parse_error:
			log.error(f"Invalid 'site_expiration_date' format: {expiration_date_str}. Error: {parse_error}")
			return False

		if getdate(nowdate()) < expiration_date:
			return False  # Site not expired

		# Site has expired, handle
		return _handle_site_expiration()

	except Exception as e:
		log.error(f"Unexpected error in site expiration check: {e}", exc_info=True)
		return False


def _handle_site_expiration():
	"""
	Display expiration message (UI & API)
	Returns True if expiration was handled
	"""
	try:
		# End user session if needed
		if hasattr(frappe, "session") and frappe.session and frappe.session.user != "Guest":
			try:
				if hasattr(frappe.local, "login_manager") and frappe.local.login_manager:
					frappe.local.login_manager.logout()
			except Exception as logout_error:
				log.warning(f"Error during logout: {logout_error}")

		# Universal HTML message
		msg = (
			"<b>🚫 Site Access Expired</b><br>"
			"Your subscription has expired.<br>"
			"Please contact support at "
			"<a href='mailto:support@idlistack.in'>support@idlistack.in</a>, "
			"<a href='https://support.idlistack.in' target='_blank'>support.idlistack.in</a>, "
			"or reach out to your account manager."
		)

		frappe.msgprint(msg, title="Site Expired", indicator="red", raise_exception=frappe.PermissionError)
		# If control continues, just to be safe:
		return True

	except Exception as e:
		log.error(f"Error handling site expiration: {e}", exc_info=True)
		# Fallback simple plain text JSON response
		frappe.local.response.update(
			{
				"type": "json",
				"http_status_code": 403,
				"message": "Site access has expired.",
				"exception": "frappe.PermissionError",
			}
		)
		return True

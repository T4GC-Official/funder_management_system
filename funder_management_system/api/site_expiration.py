import frappe
from frappe.utils import getdate, nowdate

@frappe.whitelist(allow_guest=True)
def check_site_expiration():
    site_expiration_date_in_str = frappe.local.conf.get('site_expiration_date')
    if not site_expiration_date_in_str:
        return  # No expiration date set

    site_expiration_date = getdate(site_expiration_date_in_str)
    current_date = getdate(nowdate())

    if current_date >= site_expiration_date:
        html_path = frappe.get_app_path("funder_management_system", "www", "site_expiration.html")
        with open(html_path, 'r') as file:
            html_content = file.read()

        frappe.local.response["type"] = "page"
        frappe.local.response["http_status_code"] = 403
        frappe.local.response["data"] = html_content
        return frappe.local.response

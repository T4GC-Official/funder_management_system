import frappe

def execute():
    dashboard_pages = [
        {
            "name": "Fundraising Dashboard",
            "page": "fundraising-dashboard"
        },
        {
            "name": "Donor Acquisition Dashboard",
            "page": "donor-acquisition-ma"
        },
        {
            "name": "Cashflow Dashboard",
            "page": "cashflow-dashboard"
        }
    ]

    for entry in dashboard_pages:
        if not frappe.db.exists("Dashboard List", entry["name"]):
            doc = frappe.get_doc({
                "doctype": "Dashboard List",
                "name": entry["name"],
                "dashboard": entry["page"]
            })
            doc.insert(ignore_permissions=True)
            frappe.db.commit()

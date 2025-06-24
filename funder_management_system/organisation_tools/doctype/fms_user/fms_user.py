# Copyright (c) 2025, Tech4Good Community and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.password import update_password 
from frappe import _


logger = frappe.logger("fms_user_record", allow_site=True, file_count=50)
class FMSUser(Document):
    pass


@frappe.whitelist()
def create_fms_user(doc_name):
    logger.info(f"Request for user creation received for: {doc_name}")
    user = frappe.get_doc("User Creation", doc_name)

    if not frappe.db.exists("User", user.email):
        try:
            user = frappe.get_doc({
                "doctype": "User",
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "enabled": 1,
                "send_welcome_email": 0,
                "roles": [{"role": user.role}],
                "username": user.email,
            })
            user.insert(ignore_permissions=True)
            frappe.db.commit()
            logger.info(f"User :{user.email} created successfully.")
            return {"status": True, "message": f"User {user.email} created successfully."}
        except Exception as e:
            logger.error(f"Error creating user for email {user.email}")
            frappe.throw(_("Failed to create user. Please check the logs."))
    else:
        logger.warning(f"User already exists: {user.email}")
        return {"status": True, "message": f"User {user.email} already exists."}

from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def add_custom_fields():
    custom_fields = {
        "User": [
            {
                "fieldname": "is_fundraising_admin",
                "label": "Is Fundraising Admin",
                "fieldtype": "Check",
                "insert_after": "enabled",
                "default": 0,
                "description": "Indicates whether the user is an FMS fundraising administrator."
            }
        ]
    }

    create_custom_fields(custom_fields)

    print("Custom fields added successfully.")
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def add_custom_fields():
    custom_fields = {
        "Role": [
            {
                "fieldname": "default_app",
                "label": "Default App",
                "fieldtype": "Select",
                "insert_after": "desk_access",  # Position field after desk_access
                "options": "\nFMS",             # Only one option: FMS
                "reqd": 1,
                "read_only": 0,
                "description": (
                    "This field is used to indicate that this role is associated with the FMS App. "
                    "It is set to FMS by default and cannot be changed."
                )
            }
        ],
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
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def add_custom_fields():
	custom_fields = {
		"User": [
			{
				"fieldname": "is_fundraising_admin",
				"label": "Is Fundraising Admin",
				"fieldtype": "Check",
				"insert_after": "role_profile_name",
				"default": 0,
				"read_only_depends_on": "eval:!frappe.user.has_role('Fundraising Admin')",
				"description": "Indicates whether the user is an FMS fundraising administrator.",
			}
		]
	}

	create_custom_fields(custom_fields)

	print("Custom fields added successfully.")

import frappe


def add_fms_admin_permissions_to_user_doctype():
    role = "Fundraising Admin"
    doctype = "User"

    # Define permission levels and corresponding permissions
    permissions = {
        0: {"read": 1, "write": 1, "create": 1, "delete": 1},
        1: {"read": 1, "write": 1, "if_creator": 1}
    }

    for perm_level, perm_values in permissions.items():
        try:
            # Check if permission already exists
            exists = frappe.db.exists(
                "Custom DocPerm",
                {
                    "parent": doctype,
                    "role": role,
                    "permlevel": perm_level
                }
            )
            if not exists:
                doc = frappe.get_doc({
                    "doctype": "Custom DocPerm",
                    "parent": doctype,
                    "parenttype": "DocType",
                    "parentfield": "permissions",
                    "role": role,
                    "permlevel": perm_level,
                    **perm_values
                })
                doc.insert(ignore_permissions=True)
                frappe.db.commit()
                print(
                    f"Permission added for {role} on {doctype} at level {perm_level}")
            else:
                print(
                    f"Permission already exists for {role} on {doctype} at level {perm_level}")
        except Exception as e:
            print(
                f"Error adding permission for {role} on {doctype} at level {perm_level}: {e}")


def create_roles_if_missing():
    roles = [
        "Fundraising Dashboard",
        "Donor Acquisition Dashboard",
        "Cashflow Dashboard"
    ]

    for role in roles:
        if not frappe.db.exists("Role", role):
            frappe.get_doc({
                "doctype": "Role",
                "role_name": role,
                "desk_access": 1,
                "is_custom": 1,
                "default_app": "FMS",

            }).insert(ignore_permissions=True)
            print(f"Created missing role: {role}")


def patch_roles_with_default_app(role_names, default_app="FMS"):
    """
    Ensures that each role in the list has the 'default_app' field set.

    :param role_names: List of role names to patch
    :param default_app: App name to set as default_app (defaults to "FMS")
    """
    for role_name in role_names:
        if not frappe.db.exists("Role", role_name):
            print(f"Role '{role_name}' does not exist. Skipping.")
            continue

        try:
            role_doc = frappe.get_doc("Role", role_name)

            if not role_doc.default_app:
                role_doc.default_app = default_app
                role_doc.save(ignore_permissions=True)
                print(f"Patched role '{role_name}' with default_app = '{default_app}'")
            else:
                print(f"!Role '{role_name}' already has default_app = '{role_doc.default_app}'")
        except Exception as e:
            print(f"Error patching role '{role_name}': {e}")

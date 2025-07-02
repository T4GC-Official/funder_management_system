import frappe


def create_roles_if_missing(roles):

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
                print(
                    f"Patched role '{role_name}' with default_app = '{default_app}'")
            else:
                print(
                    f"!Role '{role_name}' already has default_app = '{role_doc.default_app}'")
        except Exception as e:
            print(f"Error patching role '{role_name}': {e}")


def add_role_profile_permissions_for_fundraising_admin():
    """
    Grants read and write permission on the 'Role' doctype to the 'Fundraising Admin' role.
    """
    doctype = "Role Profile"
    role = "Fundraising Admin"
    permlevel = 0

    # Check if permission already exists
    exists = frappe.get_all("Custom DocPerm", filters={
        "parent": doctype,
        "role": role,
        "permlevel": permlevel,
        "read": 1,
        "export": 1,
    })

    if exists:
        print(
            f"Permissions already exist for role '{role}' on doctype '{doctype}'. Skipping.")
        return

    # Create permission
    docperm = frappe.get_doc({
        "doctype": "Custom DocPerm",
        "parent": doctype,
        "parenttype": "DocType",
        "parentfield": "permissions",
        "role": role,
        "read": 1,
        "write": 1,
        "permlevel": permlevel
    })

    docperm.insert(ignore_permissions=True)
    frappe.db.commit()
    print(f"Granted read/write permissions on '{doctype}' to role '{role}'")


# write a function to set default app for roles
def defalut_app_for_roles(doc, method):
    """
    Set default app for roles if not already set.
    """
    if not doc.default_app:
        doc.default_app = "FMS"
        doc.save(ignore_permissions=True)
        frappe.msgprint(f"Default app set to 'FMS' for role: {doc.name}")
    else:
        frappe.msgprint(
            f"Role {doc.name} already has a default app: {doc.default_app}")


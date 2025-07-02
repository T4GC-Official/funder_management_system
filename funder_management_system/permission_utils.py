import frappe

def add_custom_permission(doctype_name, role, permlevel=0, **permissions):
    """
    Adds custom permissions to a role for a given doctype.

    :param doctype_name: (str) Target doctype
    :param role: (str) Role to which permission is being given
    :param permlevel: (int) Permission level (default is 0)
    :param permissions: Keyword arguments like read=1, write=1, create=0, etc.
    """
    # Check if a permission entry already exists
    existing = frappe.get_all(
        "Custom DocPerm",
        filters={
            "parent": doctype_name,
            "role": role,
            "permlevel": permlevel,
        },
        fields=["name"]
    )

    if existing:
        frappe.msgprint(f"Permission already exists for '{role}' on '{doctype_name}' at level {permlevel}.")
        return

    # Construct permission dictionary
    perm_doc = {
        "doctype": "Custom DocPerm",
        "parent": doctype_name,
        "role": role,
        "permlevel": permlevel,
    }

    # Add only valid permission keys
    valid_keys = ["read", "write", "create", "delete", "submit", "cancel", "amend", "report", "export", "import", "print"]
    for key in valid_keys:
        if key in permissions:
            perm_doc[key] = int(bool(permissions[key]))  # Ensure it's 1 or 0

    frappe.get_doc(perm_doc).insert(ignore_permissions=True)
    print(f"Custom permission added: {role} → {doctype_name} (Level {permlevel})")

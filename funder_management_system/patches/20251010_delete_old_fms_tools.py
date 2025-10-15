import frappe

def execute():
    # Name of the workspace to delete
    workspace_name = "FMS Tools"

    # Check if the workspace exists before deleting
    if frappe.db.exists("Workspace", workspace_name):
        frappe.delete_doc("Workspace", workspace_name, force=1)
        frappe.db.commit()
        frappe.logger().info(f"Deleted old workspace: {workspace_name}")
    else:
        frappe.logger().info(f"Workspace '{workspace_name}' not found. Skipping deletion.")

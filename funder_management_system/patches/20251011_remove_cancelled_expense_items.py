import frappe


def execute():
	# Replace with your actual child table name
	child_table = "Expense Item Child Table"

	# Get all cancelled child records
	cancelled_items = frappe.db.get_all(
		child_table,
		filters={"utilisation_status": "Cancelled"},
		fields=["name", "parent", "parenttype", "parentfield"],
	)

	if not cancelled_items:
		frappe.logger().info("No cancelled expense items found.")
		return

	frappe.logger().info(f"Found {len(cancelled_items)} cancelled items to delete.")

	for item in cancelled_items:
		try:
			frappe.db.delete(child_table, {"name": item.name})
			if item.parenttype and item.parent:
				parent_doc = frappe.get_doc(item.parenttype, item.parent)
				parent_doc.save(ignore_permissions=True)

		except Exception:
			frappe.log_error(frappe.get_traceback(), f"Error removing cancelled child row: {item.name}")

	frappe.db.commit()
	frappe.logger().info("Removed all cancelled expense items successfully.")

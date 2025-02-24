import frappe
from funder_management_system.engagement_module.doctype.tranche_details.tranche_details import check_tranche_due_date_and_change_tranche_status
from funder_management_system.engagement_module.doctype.donor.donor import send_engagement_checklist_item_reminders

def grant_agreement_daily():
    """Enqueue the job to ensure it's logged in Scheduled Job Log."""
    frappe.enqueue(
        "funder_management_system.task.daily.run_grant_agreement_daily",
        queue="long",
        job_name="Grant Agreement Daily",
        is_async=True
    )

def donor_daily():
    """Enqueue the job to ensure it's logged in Scheduled Job Log."""
    frappe.enqueue(
        "funder_management_system.task.daily.run_donor_daily",
        queue="long",
        job_name="Donor Daily",
        is_async=True
    )

def run_grant_agreement_daily():
    """Actual function that runs the job."""
    try:
        frappe.logger().info("Running grant_agreement_daily job.")
        check_tranche_due_date_and_change_tranche_status()
        frappe.logger().info("Successfully executed grant_agreement_daily.")
    except Exception as e:
        frappe.logger().error(f"Error in grant_agreement_daily: {frappe.get_traceback()}")

def run_donor_daily():
    """Actual function that runs the job."""
    try:
        frappe.logger().info("Running donor_daily job.")
        send_engagement_checklist_item_reminders()
        frappe.logger().info("Successfully executed donor_daily.")
    except Exception as e:
        frappe.logger().error(f"Error in donor_daily: {frappe.get_traceback()}")

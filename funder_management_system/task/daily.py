from funder_management_system.donor_relationship_management.doctype.tranche_details.tranche_details import check_tranche_due_date_and_change_tranche_status
from funder_management_system.donor_relationship_management.doctype.donor.donor import send_engagement_checklist_reminders


def grant_agreement_daily():
    check_tranche_due_date_and_change_tranche_status()
    
def donor_daily():
    send_engagement_checklist_reminders()
    

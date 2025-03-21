# Copyright (c) 2025, Tech4Good Community and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document # type: ignore
logger_update = frappe.logger("update_grant_agreement", allow_site=True, file_count=10)

class GrantAgreement(Document):
    pass
def update_total_grant_amount_utilised(grant_agreement_doc):
    total_expenditure = 0
    total_received = 0
    for tranche in grant_agreement_doc.tranche_table:
        total_expenditure += tranche.total_tranche_expenditure
        total_received += tranche.tranche_amount
    if total_received == 0:
        percentage = 0
    else:
        percentage = round((total_expenditure / total_received) * 100, 2)
    logger_update.info(f"Update request for update_total_grant_amount_utilised for grant_agreement: {grant_agreement_doc.name} | updated expenditure: {total_expenditure} | updated percentage: {percentage}")
    grant_agreement_doc.total_grant_amount_utilised = total_expenditure
    grant_agreement_doc.total_tranche_amount_utilised = percentage


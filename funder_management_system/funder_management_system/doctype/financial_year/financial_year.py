# Copyright (c) 2025, Tech4Good Community and contributors
# For license information, please see license.txt
import frappe # type: ignore
from frappe.model.document import Document # type: ignore

class FinancialYear(Document):
	pass


@frappe.whitelist()
def save_financial_year(fiscal_year):
	# sourcery skip: hoist-similar-statement-from-if, remove-unnecessary-else
    if frappe.db.exists("Financial Year", fiscal_year):
        return fiscal_year
    else:
        doc = frappe.new_doc("Financial Year")
        doc.financial_year = fiscal_year
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return fiscal_year

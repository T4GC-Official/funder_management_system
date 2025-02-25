import frappe
from frappe.model.document import Document

class GrantDisbursementReceipt(Document):
    pass

@frappe.whitelist()
def create_utilisation_records(doc_name):
    """
    Creates Utilisation Ledger entries for each row in the utilisation table
    when a Grant Disbursement Receipt is submitted.
    """
    doc = frappe.get_doc("Grant Disbursement Receipt", doc_name)
    created_count = 0

    for row in doc.utilisation_table:
        if row.utilisation_record_created:
            continue
        
        utilisation_doc = frappe.get_doc({
		"doctype": "Utilisation Record",
		"grant_receipt": doc.name,
		"financial_year": doc.financial_year,
		"donor": row.donor,
		"grant": row.grant,
		"budget_plan": doc.select_budget,
		"category": row.category,
		"sub_category": row.sub_category,
		"utilised_amount": row.utilised_amount,
		"tranche_name": row.tranche
		})
        utilisation_doc.insert(ignore_permissions=True)
        
        # Create Utilisation Ledger Entry
        create_utilisation_ledger_entry(
            doc.select_budget,
            row.category,
            row.sub_category,
            row.donor,
            row.grant,
            row.tranche,
            row.utilised_amount,
            doc.name,
            row.name 
        )

        row.utilisation_record_created = 1
        created_count += 1

    if created_count > 0:
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.msgprint(f"{created_count} Utilisation Ledger Entries Created", alert=True)
    else:
        frappe.msgprint("No new Utilisation Ledger Entries were created (Already Processed)", alert=True)


def create_utilisation_ledger_entry(budget_plan, category, sub_category, donor, grant, tranche, utilised_amount, grant_disbursement, expenditure_detail):
    """
    Inserts a new record into the Utilisation Ledger and updates budget balances.
    """
    remaining_budget = get_remaining_budget(budget_plan, category, sub_category) - utilised_amount
    remaining_tranche = get_remaining_tranche(grant, tranche) - utilised_amount

    frappe.get_doc({
        "doctype": "Utilisation Ledger",
        "budget_plan": budget_plan,
        "category": category,
        "sub_category": sub_category,
        "donor": donor,
        "grant": grant,
        "grant_disbursement": grant_disbursement,
        "tranche": tranche,
        "expenditure_detail": expenditure_detail,
        "utilised_amount": utilised_amount,
        "remaining_budget": remaining_budget,
        "remaining_tranche": remaining_tranche
    }).insert(ignore_permissions=True)


def get_remaining_budget(budget_plan, category, sub_category):
    """
    Fetches the remaining budget for the given budget plan, category, and sub-category.
    """
    utilised_sum = frappe.db.sql(
        """
        SELECT SUM(utilised_amount) FROM `tabUtilisation Ledger`
        WHERE budget_plan = %s AND category = %s AND sub_category = %s
        """,
        (budget_plan, category, sub_category), as_list=True
    )[0][0] or 0

    allocated_budget = frappe.db.sql(
        """
        SELECT SUM(quarter_1_budget + quarter_2_budget + quarter_3_budget + quarter_4_budget)
        FROM `tabBudget Breakdown`
        WHERE parent = %s AND budget_category = %s AND budget_sub_category = %s
        """,
        (budget_plan, category, sub_category), as_list=True
    )[0][0] or 0

    return allocated_budget - utilised_sum


def get_remaining_tranche(grant, tranche):
    """
    Fetches the remaining tranche balance for the given donor and tranche.
    """
    tranche_amount = frappe.db.get_value("Tranche Details", {"parent": grant, "tranche_name": tranche}, "tranche_amount") or 0
    utilised_tranche = frappe.db.sql(
        """
        SELECT SUM(utilised_amount) FROM `tabUtilisation Ledger`
        WHERE `grant` = %s AND tranche = %s
        """,
        (grant, tranche), as_list=True
    )[0][0] or 0

    return tranche_amount - utilised_tranche


import frappe

import frappe

@frappe.whitelist()
def get_budget_and_tranche_details(grant):
    if not grant:
        return {"error": "Missing required parameter: grant"}

    # Fetch tranche-wise utilisation from Utilisation Ledger
    tranche_data = {}
    tranches = frappe.db.sql("""
        SELECT tranche, SUM(utilised_amount) AS total_utilised, SUM(remaining_tranche) AS remaining_tranche
        FROM `tabUtilisation Ledger`
        WHERE `grant` = %s
        GROUP BY tranche
    """, (grant,), as_dict=True)

    for t in tranches:
        tranche_data[t.tranche] = {
            "utilised": t.total_utilised or 0,
            "remaining": t.remaining_tranche or 0
        }

    # Fetch budget category-wise utilisation from Utilisation Ledger
    category_data = {}
    budget_entries = frappe.db.sql("""
        SELECT category, sub_category, SUM(utilised_amount) AS total_utilised, SUM(remaining_budget) AS remaining_budget
        FROM `tabUtilisation Ledger`
        WHERE `grant` = %s
        GROUP BY category, sub_category
    """, (grant,), as_dict=True)

    for b in budget_entries:
        category_key = f"{b.category}-{b.sub_category}"
        category_data[category_key] = {
            "utilised": b.total_utilised or 0,
            "remaining": b.remaining_budget or 0,
            "status": "Overspent" if (b.total_utilised or 0) > (b.remaining_budget or 0) else "On Track"
        }

    return {
        "tranche_data": tranche_data,
        "category_data": category_data
    }


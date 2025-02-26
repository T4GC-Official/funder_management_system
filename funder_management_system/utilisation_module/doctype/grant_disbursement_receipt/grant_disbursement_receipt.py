import frappe # type: ignore
from frappe.model.document import Document # type: ignore

frappe.utils.logger.set_log_level("DEBUG")  # Ensure debug logs are captured
logger = frappe.logger("grant_disbursement_receipt", allow_site=True, file_count=50)

class GrantDisbursementReceipt(Document):
     pass


@frappe.whitelist()
def create_utilisation_entries(document_name):
    try:
        user = frappe.session.user
        logger.info(f"{user} requested to create expenditure records for Grant Disbursement Receipt: {document_name}")
        ga_doc = frappe.get_doc("Grant Disbursement Receipt", document_name)
        utilisation_entries = []
        logger.info(f"Creating utilisation records for Grant Disbursement Receipt: {document_name}")
        count = 0
        for row in ga_doc.utilisation_child_table:
            count += 1
            if row.utilisation_record_created:
                continue
            utilisation_doc = frappe.get_doc({
                "doctype": "Utilisation Record",
                "donor": row.donor,
                "grant_agreement": ga_doc.grant_agreement,
                "category": row.category,
                "sub_category": row.sub_category,
                "utilised_amount": row.utilised_amount,
                "quarters": row.quarters,
                "budget_plan": row.budget_plan,
                "financial_year": row.financial_year,
                "utilisation_record_created": True
            })
            logger.info(f"{count} Latest log for utilisation record for grant agreement-> {ga_doc.grant_agreement} | donor name-> {row.donor}  | category-> {row.category} | sub category-> {row.sub_category} | utilised amount-> {row.utilised_amount} | financial year-> {row.financial_year} | for utilisation record: {document_name}")
            utilisation_doc.insert(ignore_permissions=True)
            utilisation_entries.append(utilisation_doc.name)
            row.db_set("expenditure_record_name", utilisation_doc.name)
            row.db_set("utilisation_record_created", True)
        frappe.db.commit()
        logger.info(f"Successfully processed {len(utilisation_entries)} records for {document_name}")
        return utilisation_entries
    except Exception as e:
        logger.error(f"Error creating utilisation records: {str(e)}")
        frappe.log_error(f"Error creating utilisation records: {str(e)}", "Utilisation Creation Error")
        return False



# # @frappe.whitelist()
# # def create_utilisation_records(doc_name):
# #     """
# #     Creates Utilisation Ledger entries for each row in the utilisation table
# #     when a Grant Disbursement Receipt is submitted.
# #     """
# #     doc = frappe.get_doc("Grant Disbursement Receipt", doc_name)
# #     created_count = 0

# #     for row in doc.utilisation_child_table:
# #         if row.utilisation_record_created:
# #             continue
# #         utilisation_doc = frappe.get_doc({
# # 		"doctype": "Utilisation Record",
# #         "donor": row.donor,   
# # 		"grant_name": doc.grant_agreement,
# #         "tranche": doc.tranche,
# #         "category": doc.category,
# #         "sub_category": doc.sub_category,
# # 		"utilised_amount": doc.utilised_amount,
# # 		"quarters": row.quarters,
# # 		"budget_plan": doc.select_budget,
# # 		"financial_year": row.financial_year,
# #         "budget_plan": row.budget_plan
# #         "utilisation_record_created": True
# # 		})
        
# #         utilisation_doc.insert(ignore_permissions=True)
        
# #         # Create Utilisation Ledger Entry
# #         create_utilisation_ledger_entry(
# #             doc.select_budget,
# #             row.category,
# #             row.sub_category,
# #             row.donor,
# #             row.grant,
# #             row.tranche,
# #             row.utilised_amount,
# #             doc.name,
# #             row.name 
# #         )
        
# #         created_count += 1

# #     if created_count > 0:
# #         doc.save(ignore_permissions=True)
# #         frappe.db.commit()
# #         frappe.msgprint(f"{created_count} Utilisation Ledger Entries Created", alert=True)
# #     else:
# #         frappe.msgprint("No new Utilisation Ledger Entries were created (Already Processed)", alert=True)




# # def create_utilisation_ledger_entry(budget_plan, category, sub_category, donor, grant, tranche, utilised_amount, grant_disbursement, expenditure_detail):
# #     """
# #     Inserts a new record into the Utilisation Ledger and updates budget balances.
# #     """
# #     remaining_budget = get_remaining_budget(budget_plan, category, sub_category) - utilised_amount
# #     remaining_tranche = get_remaining_tranche(grant, tranche) - utilised_amount

# #     frappe.get_doc({
# #         "doctype": "Utilisation Ledger",
# #         "budget_plan": budget_plan,
# #         "category": category,
# #         "sub_category": sub_category,
# #         "donor": donor,
# #         "grant": grant,
# #         "grant_disbursement": grant_disbursement,
# #         "tranche": tranche,
# #         "expenditure_detail": expenditure_detail,
# #         "utilised_amount": utilised_amount,
# #         "remaining_budget": remaining_budget,
# #         "remaining_tranche": remaining_tranche
# #     }).insert(ignore_permissions=True)


# # def get_remaining_budget(budget_plan, category, sub_category):
# #     """
# #     Fetches the remaining budget for the given budget plan, category, and sub-category.
# #     """
# #     utilised_sum = frappe.db.sql(
# #         """
# #         SELECT SUM(utilised_amount) FROM `tabUtilisation Ledger`
# #         WHERE budget_plan = %s AND category = %s AND sub_category = %s
# #         """,
# #         (budget_plan, category, sub_category), as_list=True
# #     )[0][0] or 0

# #     allocated_budget = frappe.db.sql(
# #         """
# #         SELECT SUM(quarter_1_budget + quarter_2_budget + quarter_3_budget + quarter_4_budget)
# #         FROM `tabBudget Breakdown`
# #         WHERE parent = %s AND budget_category = %s AND budget_sub_category = %s
# #         """,
# #         (budget_plan, category, sub_category), as_list=True
# #     )[0][0] or 0

# #     return allocated_budget - utilised_sum


# # def get_remaining_tranche(grant, tranche):
# #     """
# #     Fetches the remaining tranche balance for the given donor and tranche.
# #     """
# #     tranche_amount = frappe.db.get_value("Tranche Details", {"parent": grant, "tranche_name": tranche}, "tranche_amount") or 0
# #     utilised_tranche = frappe.db.sql(
# #         """
# #         SELECT SUM(utilised_amount) FROM `tabUtilisation Ledger`
# #         WHERE `grant` = %s AND tranche = %s
# #         """,
# #         (grant, tranche), as_list=True
# #     )[0][0] or 0

# #     return tranche_amount - utilised_tranche


# # @frappe.whitelist()
# # def get_budget_and_tranche_details(grant, budget_plan):
# #     if not grant or not budget_plan:
# #         return {"error": "Missing required parameters: grant and budget_plan"}

# #     # Fetch tranche-wise allocated amounts from Grant Agreement (Tranche Details)
# #     tranche_allocations = frappe.db.sql("""
# #         SELECT tranche_name, SUM(tranche_amount) AS allocated_amount
# #         FROM `tabTranche Details`
# #         WHERE parent = %s
# #         GROUP BY tranche_name
# #     """, (grant,), as_dict=True)

# #     tranche_data = {t.tranche_name: {"allocated": t.allocated_amount, "utilised": 0, "remaining": t.allocated_amount} for t in tranche_allocations}

# #     # Fetch tranche-wise utilisations from Utilisation Ledger
# #     tranche_utilisations = frappe.db.sql("""
# #         SELECT tranche, SUM(utilised_amount) AS total_utilised
# #         FROM `tabUtilisation Ledger`
# #         WHERE `grant` = %s
# #         GROUP BY tranche
# #     """, (grant,), as_dict=True)

# #     for t in tranche_utilisations:
# #         if t.tranche in tranche_data:
# #             tranche_data[t.tranche]["utilised"] = t.total_utilised or 0
# #             tranche_data[t.tranche]["remaining"] = tranche_data[t.tranche]["allocated"] - tranche_data[t.tranche]["utilised"]

# #     # Fetch category-wise and sub-category-wise allocated amounts from Budget Plan (Budget Breakdown)
# #     budget_allocations = frappe.db.sql("""
# #         SELECT budget_category, budget_sub_category, SUM(sub_total) AS allocated_amount
# #         FROM `tabBudget Breakdown`
# #         WHERE parent = %s
# #         GROUP BY budget_category, budget_sub_category
# #     """, (budget_plan,), as_dict=True)

# #     category_data = []
# #     category_dict = {}

# #     for b in budget_allocations:
# #         entry = {
# #             "category": b.budget_category,
# #             "sub_category": b.budget_sub_category,
# #             "allocated": b.allocated_amount,
# #             "utilised": 0,
# #             "remaining": b.allocated_amount,
# #             "status": "On Track"
# #         }
# #         category_data.append(entry)
# #         category_dict[(b.budget_category, b.budget_sub_category)] = entry

# #     # Fetch category-wise and sub-category-wise utilisations from Utilisation Ledger
# #     budget_utilisations = frappe.db.sql("""
# #         SELECT category, sub_category, SUM(utilised_amount) AS total_utilised
# #         FROM `tabUtilisation Ledger`
# #         WHERE `grant` = %s
# #         GROUP BY category, sub_category
# #     """, (grant,), as_dict=True)

# #     for b in budget_utilisations:
# #         found = False
# #         for entry in category_data:
# #             if entry["category"] == b.category and entry["sub_category"] == b.sub_category:
# #                 entry["utilised"] = b.total_utilised if b.total_utilised is not None else 0
# #                 entry["remaining"] = entry["allocated"] - entry["utilised"]
# #                 entry["status"] = "Overspent" if entry["remaining"] < 0 else "On Track"
# #                 found = True
# #                 break

# #         if not found:
# #             # If the category is in Utilisation Ledger but not in Budget Breakdown, initialize it
# #             category_data.append({
# #                 "category": b.category,
# #                 "sub_category": b.sub_category,
# #                 "allocated": 0,  # No allocation found in the budget
# #                 "utilised": b.total_utilised if b.total_utilised is not None else 0,
# #                 "remaining": -b.total_utilised if b.total_utilised else 0,
# #                 "status": "Overspent" if b.total_utilised > 0 else "On Track"
# #             })

# #     return {
# #         "tranche_data": tranche_data,
# #         "category_data": category_data
# #     }






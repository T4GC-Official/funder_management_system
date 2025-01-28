# Copyright (c) 2025, Tech4Good Community and contributors
# For license information, please see license.txt


import frappe
from frappe.model.document import Document

class BudgetPlanning(Document):
    def before_save(self):
        total_q1 = 0
        total_q2 = 0
        total_q3 = 0
        total_q4 = 0
        total_sub_total = 0

        for row in self.budget_breakdown:  # Get the values for each quarter, default to 0 if not set
            q1 = row.quarter_1_budget or 0
            q2 = row.quarter_2_budget or 0
            q3 = row.quarter_3_budget or 0
            q4 = row.quarter_4_budget or 0

            row.sub_total = q1 + q2 + q3 + q4

            total_q1 += q1
            total_q2 += q2
            total_q3 += q3
            total_q4 += q4
            total_sub_total += row.sub_total


        # Set the totals in the parent document fields
        try:
            self.total_quarter_1_budget = total_q1
            self.total_quarter_2_budget = total_q2
            self.total_quarter_3_budget = total_q3
            self.total_quarter_4_budget = total_q4
            self.yearly_budget = total_sub_total
        except Exception as e:
            frappe.msgprint(f'Error setting totals: {str(e)}')


@frappe.whitelist()
def get_budget_detail(template_name):
	template = frappe.get_doc("Budget Planning Template", template_name)

	child_table_data = []

	for row in template.budget_detail:
		child_table_data.append({
			"budget_category": row.budget_category,
			"budget_sub_category": row.budget_sub_category,
			"quarter_1_budget": row.quarter_1_budget,
			"quarter_2_budget": row.quarter_2_budget,
			"quarter_3_budget": row.quarter_3_budget,
			"quarter_4_budget": row.quarter_4_budget,
			"sub_total": row.sub_total
		})

	return child_table_data

# Copyright (c) 2025, Tech4Good Community and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class BudgetPlanningTemplate(Document):
	def before_save(self):
		for row in self.budget_detail:
			q1 = row.quarter_1_budget or 0
			q2 = row.quarter_2_budget or 0
			q3 = row.quarter_3_budget or 0
			q4 = row.quarter_4_budget or 0
			row.sub_total = q1 + q2 + q3 + q4


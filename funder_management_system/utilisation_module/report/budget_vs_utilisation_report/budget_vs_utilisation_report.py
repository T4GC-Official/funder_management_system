from collections import defaultdict

import frappe


def execute(filters=None):
	columns = [
		{
			"label": "Budget Plan",
			"fieldname": "budget_plan",
			"fieldtype": "Link",
			"options": "Budget Plan",
			"width": 200,
		},
		{"label": "Category Total", "fieldname": "category_total", "fieldtype": "Currency", "width": 200},
		{
			"label": "Sub Category Total",
			"fieldname": "sub_category_total",
			"fieldtype": "Currency",
			"width": 200,
		},
		{
			"label": "Q1 Allocated Budget",
			"fieldname": "total_quarter_1_budget",
			"fieldtype": "Currency",
			"width": 250,
		},
		{
			"label": "Q1 Utilised Budget",
			"fieldname": "total_quarter_1_budget_utilised",
			"fieldtype": "Currency",
			"width": 250,
		},
		{
			"label": "Q1 Utilisation %",
			"fieldname": "q1_utilisation_percentage",
			"fieldtype": "Percentage",
			"width": 150,
		},
		{
			"label": "Q2 Allocated Budget",
			"fieldname": "total_quarter_2_budget",
			"fieldtype": "Currency",
			"width": 250,
		},
		{
			"label": "Q2 Utilised Budget",
			"fieldname": "total_quarter_2_budget_utilised",
			"fieldtype": "Currency",
			"width": 250,
		},
		{
			"label": "Q2 Utilisation %",
			"fieldname": "q2_utilisation_percentage",
			"fieldtype": "Percentage",
			"width": 150,
		},
		{
			"label": "Q3 Allocated Budget",
			"fieldname": "total_quarter_3_budget",
			"fieldtype": "Currency",
			"width": 250,
		},
		{
			"label": "Q3 Utilised Budget",
			"fieldname": "total_quarter_3_budget_utilised",
			"fieldtype": "Currency",
			"width": 250,
		},
		{
			"label": "Q3 Utilisation %",
			"fieldname": "q3_utilisation_percentage",
			"fieldtype": "Percentage",
			"width": 150,
		},
		{
			"label": "Q4 Allocated Budget ",
			"fieldname": "total_quarter_4_budget",
			"fieldtype": "Currency",
			"width": 250,
		},
		{
			"label": "Q4 Utilised Budget ",
			"fieldname": "total_quarter_4_budget_utilised",
			"fieldtype": "Currency",
			"width": 250,
		},
		{
			"label": "Q4 Utilisation %",
			"fieldname": "q4_utilisation_percentage",
			"fieldtype": "Percentage",
			"width": 150,
		},
		{
			"label": "Total Allocated Budget ",
			"fieldname": "allocated_amount",
			"fieldtype": "Currency",
			"width": 250,
		},
		{
			"label": "Total Utilised Budget",
			"fieldname": "utilised_amount",
			"fieldtype": "Currency",
			"width": 200,
		},
		{
			"label": "Total Utilisation %",
			"fieldname": "utilisation_percentage",
			"fieldtype": "Percentage",
			"width": 150,
		},
	]

	data = []

	# Fetch all expense items
	expense_items = frappe.get_all(
		"Expense Item",
		fields=["budget_plan", "category", "sub_category", "utilised_amount"],
		filters={"docstatus": 1},
	)

	# Prepare Aggregation
	budget_total = defaultdict(float)  # budget_plan level
	category_total = defaultdict(lambda: defaultdict(float))  # budget_plan > category
	subcategory_total = defaultdict(
		lambda: defaultdict(lambda: defaultdict(float))
	)  # budget_plan > category > subcategory

	for item in expense_items:
		utilised = item.utilised_amount or 0
		bp = item.budget_plan or ""
		cat = item.category or ""
		subcat = item.sub_category or ""

		budget_total[bp] += utilised
		category_total[bp][cat] += utilised
		subcategory_total[bp][cat][subcat] += utilised

	# Level 0 → Budget Plan
	for bp in budget_total:
		allocated_amount = frappe.get_all(
			"Budget Plan",
			fields=[
				"yearly_budget",
				"total_quarter_1_budget",
				"total_quarter_2_budget",
				"total_quarter_3_budget",
				"total_quarter_4_budget",
			],
			filters={"name": bp},
		)

		if allocated_amount:
			yearly_total_allocated_amount_value = allocated_amount[0].get("yearly_budget", 0)
			total_quarter_1_budget = allocated_amount[0].get("total_quarter_1_budget", 0)
			total_quarter_2_budget = allocated_amount[0].get("total_quarter_2_budget", 0)
			total_quarter_3_budget = allocated_amount[0].get("total_quarter_3_budget", 0)
			total_quarter_4_budget = allocated_amount[0].get("total_quarter_4_budget", 0)
		else:
			yearly_total_allocated_amount_value = 0
			total_quarter_1_budget = 0
			total_quarter_2_budget = 0
			total_quarter_3_budget = 0
			total_quarter_4_budget = 0

		q1_utilisation = calculateUtilisation(bp, "Q1")
		q2_utilisation = calculateUtilisation(bp, "Q2")
		q3_utilisation = calculateUtilisation(bp, "Q3")
		q4_utilisation = calculateUtilisation(bp, "Q4")

		data.append(
			{
				"budget_plan": bp,
				"utilised_amount": budget_total[bp],
				"category_total": None,
				"sub_category_total": None,
				"allocated_amount": yearly_total_allocated_amount_value,
				"utilisation_percentage": formatPercentage(
					calculatePercentageOfAllocatedAmount(
						budget_total, bp, yearly_total_allocated_amount_value
					)
				),
				"total_quarter_1_budget": total_quarter_1_budget,
				"total_quarter_1_budget_utilised": q1_utilisation,
				"q1_utilisation_percentage": formatPercentage(
					calculatePercentage(q1_utilisation, total_quarter_1_budget)
				),
				"total_quarter_2_budget": total_quarter_2_budget,
				"total_quarter_2_budget_utilised": q2_utilisation,
				"q2_utilisation_percentage": formatPercentage(
					calculatePercentage(q2_utilisation, total_quarter_2_budget)
				),
				"total_quarter_3_budget": total_quarter_3_budget,
				"total_quarter_3_budget_utilised": q3_utilisation,
				"q3_utilisation_percentage": formatPercentage(
					calculatePercentage(q3_utilisation, total_quarter_3_budget)
				),
				"total_quarter_4_budget": total_quarter_4_budget,
				"total_quarter_4_budget_utilised": q4_utilisation,
				"q4_utilisation_percentage": formatPercentage(
					calculatePercentage(q4_utilisation, total_quarter_4_budget)
				),
				"indent": 0,
			}
		)

		# Level 1 → Category
		for cat in category_total[bp]:
			# Fetch sub_total from budget_breakdown where parent is budget plan
			budget_breakdown_items = frappe.get_all(
				"Budget Breakdown",
				fields=["sub_total"],
				filters={"parent": bp, "budget_category": cat, "docstatus": 1},
			)

			allocated_cat_amount = sum(item["sub_total"] for item in budget_breakdown_items)
			data.append(
				{
					"budget_plan": cat,
					"category_total": category_total[bp][cat],
					"sub_category_total": None,
					"utilised_amount": None,
					"allocated_amount": allocated_cat_amount,
					"total_quarter_1_budget": None,
					"total_quarter_1_budget_utilised": None,
					"total_quarter_2_budget": None,
					"total_quarter_2_budget_utilised": None,
					"total_quarter_3_budget": None,
					"total_quarter_3_budget_utilised": None,
					"total_quarter_4_budget": None,
					"total_quarter_4_budget_utilised": None,
					"indent": 1,
				}
			)

			# Level 2 → Sub Category
			for subcat in subcategory_total[bp][cat]:
				allocated_subcat_amount = 0
				budget_breakdown_items = frappe.get_all(
					"Budget Breakdown",
					fields=["sub_total"],
					filters={"parent": bp, "budget_sub_category": subcat, "docstatus": 1},
				)

				if budget_breakdown_items:
					allocated_subcat_amount = budget_breakdown_items[0].get("sub_total", 0)

				data.append(
					{
						"budget_plan": subcat,
						"category_total": None,
						"sub_category_total": subcategory_total[bp][cat][subcat],
						"utilised_amount": None,
						"allocated_amount": allocated_subcat_amount,
						"total_quarter_1_budget": None,
						"total_quarter_1_budget_utilised": None,
						"total_quarter_2_budget": None,
						"total_quarter_2_budget_utilised": None,
						"total_quarter_3_budget": None,
						"total_quarter_3_budget_utilised": None,
						"total_quarter_4_budget": None,
						"total_quarter_4_budget_utilised": None,
						"indent": 2,
					}
				)

	return columns, data


def calculateUtilisation(bp, quarter):
	return sum(
		item["utilised_amount"] or 0
		for item in frappe.get_all(
			"Expense Item",
			fields=["utilised_amount"],
			filters={"budget_plan": bp, "quarters": quarter, "docstatus": 1},
		)
	)


def calculatePercentageOfAllocatedAmount(budget_total, bp, allocated_amount_value):
	percetage = calculatePercentage(budget_total[bp], allocated_amount_value)
	return percetage


def calculatePercentage(utiliased_amount, allocated_amount_value):
	percetage = (
		round((utiliased_amount / allocated_amount_value) * 100, 2) if allocated_amount_value != 0 else 0
	)
	return percetage


def formatPercentage(percentage):
	icon = "equals" if percentage == 100 else ("down" if percentage < 100 else "up")
	color = "green" if percentage <= 100 else "red"
	return f'{percentage}% <span style="color: {color}; font-weight: bold;"><i class="fa fa-arrow-{icon}"></i> </span> '

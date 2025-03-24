# Copyright (c) 2025, Tech4Good Community and contributors
# For license information, please see license.txt

import frappe
from frappe import _

import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "name", "label": "Budget Plan / Budget Category / Budget Sub-Category", "fieldtype": "Data", "width": 350},
        {"fieldname": "budget_plan_link", "label": "",  "fieldtype": "HTML"},
        {"fieldname": "docstatus", "label": "Status", "fieldtype": "Data"},
        {"fieldname": "financial_year", "label": "Financial Year", "fieldtype": "Link", "options": "Financial Year"},
        {"fieldname": "currency", "label": "Currency", "fieldtype": "Link", "options": "Currency"},
        {"fieldname": "total_quarter_1_budget", "label": "Q1 Budget", "fieldtype": "Currency"},
        {"fieldname": "total_quarter_2_budget", "label": "Q2 Budget", "fieldtype": "Currency"},
        {"fieldname": "total_quarter_3_budget", "label": "Q3 Budget", "fieldtype": "Currency"},
        {"fieldname": "total_quarter_4_budget", "label": "Q4 Budget", "fieldtype": "Currency"},
        {"fieldname": "subtotal", "label": "Sub Total", "fieldtype": "Currency"},
        {"fieldname": "total", "label": "Total", "fieldtype": "Currency"},
        {"fieldname": "indent", "label": "Indent", "fieldtype": "Int", "hidden": 1},
    ]

    data = []

    # Fetch all Budget Plans
    budget_plans = frappe.get_all(
        "Budget Plan",
        filters={"docstatus": ("in", (0, 1, 2))},
        fields=["name", "docstatus", "financial_year", "currency",
                "total_quarter_1_budget", "total_quarter_2_budget", "total_quarter_3_budget",
                "total_quarter_4_budget", "yearly_budget"]
    )

    # Process Budget Plans
    for plan in budget_plans:
        # Convert docstatus to human-readable format
        status_map = {0: "Draft", 1: "Submitted", 2: "Cancelled"}
        plan["docstatus"] = status_map.get(plan["docstatus"], "Unknown")

        # Append the Budget Plan as the main parent row (Level 0)
        data.append({
             "name": plan['name'],
            "docstatus": f"<strong>{plan['docstatus']}</strong>",
            "financial_year": plan["financial_year"],
            "currency": plan["currency"],
            "total_quarter_1_budget": plan["total_quarter_1_budget"],
            "total_quarter_2_budget": plan["total_quarter_2_budget"],
            "total_quarter_3_budget": plan["total_quarter_3_budget"],
            "total_quarter_4_budget": plan["total_quarter_4_budget"],
            "subtotal": "--",
             "budget_plan_link": f'<a href="/app/budget-plan/{plan["name"]}" target="_blank" title="View Budget Plan">View</a>',
            "total": plan["yearly_budget"],
            "indent": 0
        })

        # Fetch and group Budget Breakdown by category and sub-category
        budget_breakdowns = frappe.get_all(
            "Budget Breakdown",
            filters={"parent": plan["name"]},
            fields=["budget_category","budget_sub_category", "quarter_1_budget", "quarter_2_budget", 
                    "quarter_3_budget", "quarter_4_budget"]
        )

        category_totals = {}

        for breakdown in budget_breakdowns:
            category = breakdown["budget_category"]
            sub_category = breakdown["budget_sub_category"]

            # If category is not yet in the dictionary, initialize it
            if category not in category_totals:
                category_totals[category] = {
                    "total_quarter_1_budget": 0,
                    "total_quarter_2_budget": 0,
                    "total_quarter_3_budget": 0,
                    "total_quarter_4_budget": 0,
                    "sub_categories": {}
                }

            # Sum category-level totals
            category_totals[category]["total_quarter_1_budget"] += breakdown["quarter_1_budget"]
            category_totals[category]["total_quarter_2_budget"] += breakdown["quarter_2_budget"]
            category_totals[category]["total_quarter_3_budget"] += breakdown["quarter_3_budget"]
            category_totals[category]["total_quarter_4_budget"] += breakdown["quarter_4_budget"]

            # Add sub-category data under its category
            if sub_category not in category_totals[category]["sub_categories"]:
                category_totals[category]["sub_categories"][sub_category] = {
                    "total_quarter_1_budget": 0,
                    "total_quarter_2_budget": 0,
                    "total_quarter_3_budget": 0,
                    "total_quarter_4_budget": 0
                }

            # Sum sub-category values
            category_totals[category]["sub_categories"][sub_category]["total_quarter_1_budget"] += breakdown["quarter_1_budget"]
            category_totals[category]["sub_categories"][sub_category]["total_quarter_2_budget"] += breakdown["quarter_2_budget"]
            category_totals[category]["sub_categories"][sub_category]["total_quarter_3_budget"] += breakdown["quarter_3_budget"]
            category_totals[category]["sub_categories"][sub_category]["total_quarter_4_budget"] += breakdown["quarter_4_budget"]

        # Append budget categories under the parent Budget Plan
        for category, cat_totals in category_totals.items():
            category_subtotal = (
                cat_totals["total_quarter_1_budget"] + cat_totals["total_quarter_2_budget"] +
                cat_totals["total_quarter_3_budget"] + cat_totals["total_quarter_4_budget"]
            )

            data.append({
                "name": f"📌 {category}",
                "docstatus": "",
                "financial_year": "",
                "currency": "",
                "total_quarter_1_budget": cat_totals["total_quarter_1_budget"],
                "total_quarter_2_budget": cat_totals["total_quarter_2_budget"],
                "total_quarter_3_budget": cat_totals["total_quarter_3_budget"],
                "total_quarter_4_budget": cat_totals["total_quarter_4_budget"],
                "total": category_subtotal,
                "indent": 1  # Indent to show category under budget plan
            })

            # Append subcategories under the category
            for sub_category, sub_totals in cat_totals["sub_categories"].items():
                sub_total = (
                    sub_totals["total_quarter_1_budget"] + sub_totals["total_quarter_2_budget"] +
                    sub_totals["total_quarter_3_budget"] + sub_totals["total_quarter_4_budget"]
                )

                data.append({
                    "name": f"🔹 {sub_category}",
                    "docstatus": "",
                    "financial_year": "",
                    "currency": "",
                    "total_quarter_1_budget": sub_totals["total_quarter_1_budget"],
                    "total_quarter_2_budget": sub_totals["total_quarter_2_budget"],
                    "total_quarter_3_budget": sub_totals["total_quarter_3_budget"],
                    "total_quarter_4_budget": sub_totals["total_quarter_4_budget"],
                    "subtotal": sub_total,
                    "total": "--",
                    "indent": 2  # Indent to show subcategory under category
                })

    return columns, data


def get_columns() -> list[dict]:
	"""Return columns for the report.

	One field definition per column, just like a DocType field definition.
	"""
	return [
		{
			"label": _("Column 1"),
			"fieldname": "column_1",
			"fieldtype": "Data",
		},
		{
			"label": _("Column 2"),
			"fieldname": "column_2",
			"fieldtype": "Int",
		},
	]


def get_data() -> list[list]:
	"""Return data for the report.

	The report data is a list of rows, with each row being a list of cell values.
	"""
	return [
		["Row 1", 1],
		["Row 2", 2],
	]

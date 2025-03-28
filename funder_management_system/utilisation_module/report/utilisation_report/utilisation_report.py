import frappe
from collections import defaultdict


def execute(filters=None):
    columns = [
        {"label": "Budget Plan", "fieldname": "budget_plan",
            "fieldtype": "Link", "options": "Budget Plan", "width": 200},
        {"label": "Category Total", "fieldname": "category_total",
            "fieldtype": "Currency", "width": 200},
        {"label": "Sub Category Total", "fieldname": "sub_category_total",
            "fieldtype": "Currency", "width": 200},
        {"label": "Utilised Amount", "fieldname": "utilised_amount",
            "fieldtype": "Currency", "width": 200},
        {"label": "Allocated Amount", "fieldname": "allocated_amount",
            "fieldtype": "Currency", "width": 250},
        {"label": "Utilisation %", "fieldname": "utilisation_percentage",
            "fieldtype": "Percentage", "width": 150}
    ]

    data = []

    # Fetch all expense items
    expense_items = frappe.get_all("Expense Item",
                                   fields=["budget_plan", "category",
                                           "sub_category", "utilised_amount"]
                                   )

    # Prepare Aggregation
    budget_total = defaultdict(float)                   # budget_plan level
    category_total = defaultdict(
        lambda: defaultdict(float))   # budget_plan > category
    subcategory_total = defaultdict(lambda: defaultdict(
        lambda: defaultdict(float)))   # budget_plan > category > subcategory

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
            fields=["yearly_budget"],
            filters={"name": bp, "docstatus": 1}
        )

        if allocated_amount:
            allocated_amount_value = allocated_amount[0].get(
                "yearly_budget", 0)
        else:
            allocated_amount_value = 0

        data.append({
            "budget_plan": bp,
            "utilised_amount": budget_total[bp],
            "category_total": None,
            "sub_category_total": None,
            "allocated_amount": allocated_amount_value,
            "utilisation_percentage": formatPercentage(calculatePercentage(budget_total, bp, allocated_amount_value)),
            "indent": 0
        })

        # Level 1 → Category
        for cat in category_total[bp]:
            # Fetch sub_total from budget_breakdown where parent is budget plan
            budget_breakdown_items = frappe.get_all(
                "Budget Breakdown",
                fields=["sub_total"],
                filters={"parent": bp, "budget_category": cat, "docstatus": 1}
            )

            allocated_cat_amount = sum(item["sub_total"]
                                       for item in budget_breakdown_items)
            data.append({
                "budget_plan": cat,
                "category_total": category_total[bp][cat],
                "sub_category_total": None,
                "utilised_amount": None,
                "allocated_amount": allocated_cat_amount,
                "indent": 1,
            })

            # Level 2 → Sub Category
            for subcat in subcategory_total[bp][cat]:
                allocated_subcat_amount = 0
                budget_breakdown_items = frappe.get_all(
                    "Budget Breakdown",
                    fields=["sub_total"],
                    filters={"parent": bp,
                             "budget_sub_category": subcat, "docstatus": 1}
                )

                if budget_breakdown_items:
                    allocated_subcat_amount = budget_breakdown_items[0].get(
                        "sub_total", 0)

                data.append({
                    "budget_plan": subcat,
                    "category_total": None,
                    "sub_category_total": subcategory_total[bp][cat][subcat],
                    "utilised_amount": None,
                    "allocated_amount": allocated_subcat_amount,
                    "indent": 2,
                })

    return columns, data


def calculatePercentage(budget_total, bp, allocated_amount_value):
    percetage = round((budget_total[bp] / allocated_amount_value)
                      * 100, 2) if allocated_amount_value != 0 else 0
    return percetage


def formatPercentage(percentage):
    icon = 'equals' if percentage == 100 else ('down' if percentage < 100 else 'up')
    color = 'green' if percentage <= 100 else 'red'
    return '{}% <span style="color: {}; font-weight: bold;"><i class="fa fa-arrow-{}"></i> </span> '.format(
        percentage,
        color,
        icon
    )

import frappe
from frappe import _
from frappe.utils.dashboard import cache_source

@frappe.whitelist()
@cache_source
def get(
    chart_name=None,
    chart=None,
    no_cache=None,
    filters=None,
    from_date=None,
    to_date=None,
    timespan=None,
    time_interval=None,
    heatmap_year=None,
):
    if not chart:
        frappe.log_error("Chart parameter is missing or None.", "Chart Parameter Error")
        chart_name = "budget_plan_overutilization_donut"

    labels, yearly_budgets, overutilized_amounts, overutilization_percentages = [], [], [], []

    result = frappe.db.sql("""
        SELECT 
            bp.name AS budget_plan,
            bp.financial_year,
            bp.yearly_budget,
            COALESCE(SUM(ei.utilised_amount), 0) AS utilized_amount,
            (COALESCE(SUM(ei.utilised_amount), 0) - bp.yearly_budget) AS overutilized_amount,
            ROUND(((COALESCE(SUM(ei.utilised_amount), 0) - bp.yearly_budget) / bp.yearly_budget) * 100, 2) AS overutilization_percent
        FROM `tabBudget Plan` bp
        LEFT JOIN `tabExpense Item` ei ON ei.budget_plan = bp.name AND ei.docstatus = 1
        WHERE bp.docstatus = 1 AND bp.yearly_budget > 0
        GROUP BY bp.name
        HAVING utilized_amount > bp.yearly_budget
    """, as_dict=True)

    for row in result:
        labels.append(f"{row.financial_year}")
        yearly_budgets.append(row.yearly_budget)
        overutilized_amounts.append(row.overutilized_amount)
        overutilization_percentages.append(row.overutilization_percent)

    return {
        "labels": labels,
        "datasets": [
            {
                "name": _("Yearly Budget"),
                "values": yearly_budgets,
                "type": "bar",
                "color": "#17a2b8"
            },
            {
                "name": _("Overutilized Amount"),
                "values": overutilized_amounts,
                "type": "bar",
                "color": "#dc3545"
            }
        ],
        "custom_data": {
            "overutilization_percent": overutilization_percentages
        }
    }

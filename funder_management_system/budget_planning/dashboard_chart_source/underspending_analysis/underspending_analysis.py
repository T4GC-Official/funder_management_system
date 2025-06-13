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
        chart_name = "budget_plan_underutilization_combo"

    labels = []
    yearly_budgets = []
    utilized_amounts = []
    underutilization_percentages = []
    

    result = frappe.db.sql("""
        SELECT 
            bp.name AS budget_plan,
            bp.financial_year,
            bp.yearly_budget,
            COALESCE(SUM(ei.utilised_amount), 0) AS utilized_amount,
            ROUND(((bp.yearly_budget - COALESCE(SUM(ei.utilised_amount), 0)) / bp.yearly_budget) * 100, 2) AS underutilization_percent
        FROM `tabBudget Plan` bp
        LEFT JOIN `tabExpense Item` ei ON ei.budget_plan = bp.name AND ei.docstatus = 1
        WHERE bp.docstatus = 1 AND bp.yearly_budget > 0
        GROUP BY bp.name
        HAVING utilized_amount < bp.yearly_budget
    """, as_dict=True)

    for row in result:
        labels.append(row.financial_year)
        yearly_budgets.append(row.yearly_budget)
        utilized_amounts.append(row.utilized_amount)
        underutilization_percentages.append(row.underutilization_percent)

    return {
        "labels": labels,
        "datasets": [
            {
                "name": _("Yearly Budget"),
                "values": yearly_budgets,
                "chartType": "bar"
            },
            {
                "name": _("Utilized Amount"),
                "values": utilized_amounts,
                "chartType": "line"
            }
        ],
        "type": "axis-mixed",
        "colors": ["#007bff", "#28a745"],
        "lineOptions": {
            "regionFill": 0
        },
        "barOptions": {
            "stacked": 0
        },
         "custom_data": {
            "underutilization_percent": underutilization_percentages
        }
       
    }

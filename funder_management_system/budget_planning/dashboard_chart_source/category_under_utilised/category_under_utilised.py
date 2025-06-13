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
    budget_plan=None,
):
    if not chart:
        frappe.log_error("Chart parameter is missing or None.", "Chart Parameter Error")
        chart_name = "default_underutilization_chart"

    labels, allocated_values, utilized_values, underutilization_percentages = [], [], [], []

    filters = frappe.parse_json(filters) if filters else {}
    filters["docstatus"] = 1

    budget_plans = frappe.get_all(
        "Budget Plan",
        filters=filters,
        fields=["name", "financial_year", "currency"]
    )

    if not budget_plans:
        frappe.log_error("No budget plans found with the provided filters.", "Budget Plan Fetch Error")

    result = frappe.db.sql("""
        SELECT ei.category, 
               SUM(ei.utilised_amount) AS total_utilized_amount, 
               SUM(bb.sub_total) AS total_allocated_amount
        FROM `tabExpense Item` ei
        JOIN `tabBudget Plan` bp ON ei.budget_plan = bp.name
        JOIN `tabBudget Breakdown` bb ON ei.category = bb.budget_category AND ei.budget_plan = bb.parent
        WHERE bp.docstatus = 1 
          AND ei.docstatus = 1 
        GROUP BY ei.category
        HAVING total_utilized_amount < total_allocated_amount
    """, as_dict=True)

    if not result:
        frappe.log_error("No results returned for underutilization query.", "SQL Query Result Error")

    for row in result:
        category = row["category"]
        allocated = float(row["total_allocated_amount"])
        utilized = float(row["total_utilized_amount"])
        percent = round(((allocated - utilized) / allocated) * 100, 2)

        labels.append(f"{category} ({percent}% under)")
        allocated_values.append(allocated)
        utilized_values.append(utilized)
        underutilization_percentages.append(percent)

    return {
        "labels": labels,
        "datasets": [
            {
                "name": _("Allocated Amount"),
                "values": allocated_values,
                "barWidth": 10,
                "type": "bar",
                "color": "#007bff",
            },
            {
                "name": _("Utilized Amount"),
                "values": utilized_values,
                "barWidth": 10,
                "type": "bar",
                "color": "#ffc107",  # Yellow for underutilized
            }
        ],
        "custom_data": {
            "underutilization_percent": underutilization_percentages
        }
    }

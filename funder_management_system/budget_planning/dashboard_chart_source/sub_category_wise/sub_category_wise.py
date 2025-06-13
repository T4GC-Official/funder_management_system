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
    labels, datapoints = [], []

    # Parse filters if provided (optional)
    filters = frappe.parse_json(filters) if filters else {}

    # Handle the budget_plan filter if provided
    if budget_plan:
        filters['budget_plan'] = budget_plan  # Apply the filter

    # Query to get the sum of sub_total grouped by budget_category, filtered by the budget_plan
    query = """
        SELECT 
            bd.budget_sub_category,
            SUM(bd.sub_total) AS total_sub_total
        FROM `tabBudget Breakdown` bd
        JOIN `tabBudget Plan` bp ON bd.parent = bp.name
        WHERE bp.docstatus = 1
    """

    # If a budget_plan filter is provided, add it to the WHERE clause
    if budget_plan:
        query += " AND bp.name = %s"

    query += " GROUP BY bd.budget_sub_category;"

    # Execute the query, passing the budget_plan if needed
    # Ensure that we pass a tuple for the query parameters
    data = frappe.db.sql(query, (budget_plan,) if budget_plan else (), as_dict=True)

    # Extract labels and datapoints from the query result
    labels = [row['budget_sub_category'] for row in data]
    datapoints = [row['total_sub_total'] for row in data]

    # Return chart data in the format required by Frappe Dashboard
    return {
        "labels": labels,
        "datasets": [
            {
                "name": _("Total by Budget Sub-Category"),
                "values": datapoints,
            }
        ],
    }

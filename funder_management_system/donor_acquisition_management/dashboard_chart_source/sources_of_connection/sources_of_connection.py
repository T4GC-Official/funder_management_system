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
    # Fetch counts of leads grouped by thematic_area from child table
    results = frappe.db.sql("""
        SELECT source_of_connection, COUNT(DISTINCT parent) AS count
        FROM `tabSource of Connection Child`
        GROUP BY source_of_connection
    """, as_dict=True)

    labels = [row["source_of_connection"] for row in results]
    datapoints = [row["count"] for row in results]

    return {
        "labels": labels,
        "datasets": [
            {
                "name": _("Leads by Sources of Connection"),
                "values": datapoints
            }
        ],

    }

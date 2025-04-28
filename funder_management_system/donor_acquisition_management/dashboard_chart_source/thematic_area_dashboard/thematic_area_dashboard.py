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
        SELECT thematic_area, COUNT(DISTINCT parent) AS count
        FROM `tabThematic Area Child`
        GROUP BY thematic_area
    """, as_dict=True)

    labels = [row["thematic_area"] for row in results]
    datapoints = [row["count"] for row in results]

    return {
        "labels": labels,
        "datasets": [
            {
                "name": _("Leads by Thematic Area"),
                "values": datapoints
            }
        ],
        "type": "bar"
    }

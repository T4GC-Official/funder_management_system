import frappe
from frappe import _
from frappe.utils.dashboard import cache_source
from funder_management_system.utils import get_current_financial_year

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
    financial_year=None,
):
    if financial_year:
        results = frappe.db.sql("""
            SELECT child.source_of_connection, COUNT(DISTINCT child.parent) AS count
            FROM `tabSource of Connection Child` AS child
            JOIN `tabOrganisation Lead` AS parent_doc ON child.parent = parent_doc.name
            WHERE parent_doc.financial_year_of_reachout = %s
            GROUP BY child.source_of_connection
        """, (financial_year,), as_dict=True)

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
    else:
        return {
            "labels": [],
            "datasets": [
                {
                    "name": _("Leads by Sources of Connection"),
                    "values": []
                }
            ],
        }

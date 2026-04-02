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
):
	current_fy = get_current_financial_year()

	data = frappe.db.sql(
		"""
        SELECT ga.donor_name, SUM(td.tranche_amount) AS grant_received
        FROM `tabGrant Agreement` ga
        JOIN `tabTranche Details` td ON ga.name = td.parent
        WHERE td.tranche_status IN ('Received - On Time', 'Received - Delayed')
          AND td.tranche_financial_year = %s
        GROUP BY ga.donor_name
        ORDER BY grant_received DESC
        LIMIT 5
    """,
		(current_fy,),
		as_dict=True,
	)
	labels = [row["donor_name"] for row in data]
	datapoints = [row["grant_received"] for row in data]
	return {
		"labels": labels,
		"datasets": [{"name": _("Top 5 Donors"), "values": datapoints}],
	}

import frappe
from frappe import _

from funder_management_system.utils import (
	get_fy_date_ranges_from_doctype,
	normalize_financial_years,
	total_conversion,
)

logger = frappe.logger("dashboard", allow_site=True, file_count=10)


@frappe.whitelist()
def get_number_cards(financial_years=None):
	"""Returns summary cards for the dashboard."""
	logger.info("Fetching number cards")
	cards = [
		get_total_funds_raised(financial_years),
		get_total_expenditure(financial_years),
		get_total_active_donors(financial_years),
		get_total_active_grant_agreements(financial_years),
	]

	# Ensure each card has a label and fieldtype
	for card in cards:
		card.setdefault("label", _("Value"))
		card.setdefault("fieldtype", "Data")

	return cards


@frappe.whitelist()
def get_total_funds_raised(financial_years=None):
	years = normalize_financial_years(financial_years)
	logger.info(f"[Total Funds] Normalized Financial Years: {years}")

	if not years:
		logger.warning("[Total Funds] No financial years provided or normalization failed.")
		return {"value": "0.00", "label": _("Total Funds Raised"), "fieldtype": "Currency"}

	placeholders = ", ".join(["%s"] * len(years))
	query = f"""
        SELECT SUM(tranche_amount)
        FROM `tabTranche Details`
        WHERE tranche_status IN ('Received - On Time', 'Received - Delayed')
        AND tranche_financial_year IN ({placeholders})
    """

	try:
		raw_total = frappe.db.sql(query, tuple(years))[0][0] or 0.0
		logger.info(f"[Total Funds] Total funds raised: {raw_total} for years: {years}")

		converted = total_conversion(raw_total)
		currency = frappe.defaults.get_global_default("currency") or "INR"
		symbol = frappe.db.get_value("Currency", currency, "symbol") or currency

		return {
			"value": f"{symbol} {converted['value']}",
			"label": _("Total Funds Raised"),
			"fieldtype": "Data",  # Since it's now a string with suffix
		}
	except Exception as e:
		logger.error(f"[Total Funds] Error fetching funds raised: {e}")
		frappe.log_error(frappe.get_traceback(), "Error in get_total_funds_raised")
		return {"value": "0.00", "label": _("Total Funds Raised"), "fieldtype": "Data"}


@frappe.whitelist()
def get_total_expenditure(financial_years=None):
	"""Returns total expenditure as a card."""
	years = normalize_financial_years(financial_years)
	logger.info(f"[Total Expenditure] Normalized Financial Years: {years}")

	if not years:
		logger.warning("[Total Expenditure] No financial years provided or normalization failed.")
		return {"value": "0.00", "label": _("Total Expenditure"), "fieldtype": "Currency"}

	placeholders = ", ".join(["%s"] * len(years))
	query = f"""
        SELECT SUM(utilised_amount)
        FROM `tabExpense Item`
        WHERE docstatus = 1 AND financial_year IN ({placeholders})
    """

	try:
		raw_total = frappe.db.sql(query, tuple(years))[0][0] or 0.0
		logger.info(f"[Total Expenditure] Total expenditure: {raw_total} for years: {years}")

		converted = total_conversion(raw_total)
		currency = frappe.defaults.get_global_default("currency") or "INR"
		symbol = frappe.db.get_value("Currency", currency, "symbol") or currency

		return {
			"value": f"{symbol} {converted['value']}",
			"label": _("Total Expenditure"),
			"fieldtype": "Data",  # Since it's now a string with suffix
		}
	except Exception as e:
		logger.error(f"[Total Expenditure] Error fetching expenditure: {e}")
		frappe.log_error(frappe.get_traceback(), "Error in get_total_expenditure")
		return {"value": "0.00", "label": _("Total Expenditure"), "fieldtype": "Data"}


@frappe.whitelist()
def get_total_active_donors(financial_years=None):
	years = normalize_financial_years(financial_years)

	if not years:
		return {"value": 0, "label": "Active Donors", "fieldtype": "Int"}

	fy_ranges = get_fy_date_ranges_from_doctype(years)
	donor_set = set()

	for start, end in fy_ranges:
		rows = frappe.db.sql(
			"""
            SELECT DISTINCT donor_name
            FROM `tabGrant Agreement`
            WHERE grant_agreement_start_date <= %s
              AND grant_agreement_end_date >= %s
        """,
			(end, start),
			as_dict=True,
		)
		donor_set.update([r["donor_name"] for r in rows if r["donor_name"]])

	return {"value": len(donor_set), "label": "Active Donors", "fieldtype": "Int"}


@frappe.whitelist()
def get_total_active_grant_agreements(financial_years=None):
	years = normalize_financial_years(financial_years)

	if not years:
		return {"value": 0, "label": "Active Grant Agreements", "fieldtype": "Int"}

	fy_ranges = get_fy_date_ranges_from_doctype(years)
	agreement_ids = set()

	for start, end in fy_ranges:
		rows = frappe.db.sql(
			"""
            SELECT name
            FROM `tabGrant Agreement`
            WHERE grant_agreement_start_date <= %s
              AND grant_agreement_end_date >= %s
        """,
			(end, start),
			as_dict=True,
		)
		agreement_ids.update([r["name"] for r in rows])

	return {"value": len(agreement_ids), "label": "Active Grant Agreements", "fieldtype": "Int"}


@frappe.whitelist()
def get_top_donors(financial_years=None):
	years = normalize_financial_years(financial_years)

	if not years:
		return {"labels": [], "datasets": [{"name": _("Top Donors"), "values": []}]}

	placeholders = ", ".join(["%s"] * len(years))
	query = f"""
        SELECT ga.donor_name, SUM(td.tranche_amount) AS grant_received
        FROM `tabGrant Agreement` ga
        JOIN `tabTranche Details` td ON ga.name = td.parent
        WHERE td.tranche_status IN ('Received - On Time', 'Received - Delayed')
        AND td.tranche_financial_year IN ({placeholders})
        GROUP BY ga.donor_name
        ORDER BY grant_received DESC
        LIMIT 10
    """

	data = frappe.db.sql(query, tuple(years), as_dict=True)

	labels = [row["donor_name"] for row in data]
	datapoints = [row["grant_received"] for row in data]

	return {
		"labels": labels,
		"datasets": [{"name": _("Top 10 Donors"), "values": datapoints, "fieldtype": "Currency"}],
	}


@frappe.whitelist()
def get_funds_received_vs_utilised(financial_years=None):
	years = normalize_financial_years(financial_years)

	if not years:
		return {"labels": [], "datasets": []}

	fy_ranges = get_fy_date_ranges_from_doctype(years)

	agreement_data = {}

	for start, end in fy_ranges:
		rows = frappe.db.sql(
			"""
            SELECT name, donor, total_tranche_amount_received, total_grant_amount_utilised
            FROM `tabGrant Agreement`
            WHERE grant_agreement_start_date <= %s
            AND grant_agreement_end_date >= %s
            ORDER BY total_tranche_amount_received DESC
        """,
			(end, start),
			as_dict=True,
		)

		for row in rows:
			key = f"{row.donor}"
			agreement_data[key] = {
				"received": row.total_tranche_amount_received or 0,
				"utilised": row.total_grant_amount_utilised or 0,
			}

	labels = list(agreement_data.keys())
	received = [agreement_data[k]["received"] for k in labels]
	utilised = [agreement_data[k]["utilised"] for k in labels]

	return {
		"labels": labels,
		"datasets": [
			{"name": _("Funds Received"), "values": received},
			{"name": _("Funds Utilised"), "values": utilised},
		],
	}

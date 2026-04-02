import json

import frappe
from frappe import _

from funder_management_system.utils import normalize_financial_years, total_conversion

dashboard_logger = frappe.logger("dashboard", allow_site=True, file_count=10)


@frappe.whitelist()
def get_budget_cards(financial_years=None):
	dashboard_logger.info("Fetching budget cards for financial years: %s", financial_years)

	cards = [
		get_total_budget(financial_years),
		# add more cards here
	]

	# Ensure each card has fallback values
	for card in cards:
		card.setdefault("label", _("Value"))
		card.setdefault("fieldtype", "Currency")

	return cards


@frappe.whitelist()
def get_total_budget(financial_years=None):
	years = normalize_financial_years(financial_years)
	if not years:
		return {"value": "0.00", "label": _("Total Budget"), "fieldtype": "Currency"}

	placeholders = ",".join(["%s"] * len(years))
	results = frappe.db.sql(
		f"""
        SELECT
            bp.currency,
            SUM(bp.yearly_budget) AS total_budget
        FROM `tabBudget Plan` bp
        WHERE bp.docstatus = 1 AND bp.financial_year IN ({placeholders})
        GROUP BY bp.currency
    """,
		tuple(years),
		as_dict=True,
	)

	if not results:
		return {"value": "0.00", "label": _("Total Budget"), "fieldtype": "Currency"}

	# For simplicity, assuming only one currency exists in the result
	total_budget = results[0]["total_budget"] or 0
	currency = results[0]["currency"] or "INR"
	symbol = frappe.db.get_value("Currency", currency, "symbol") or ""

	converted = total_conversion(total_budget)

	return {"value": f"{symbol} {converted['value']}", "label": _("Total Budget"), "fieldtype": "Currency"}


@frappe.whitelist()
def get_budget_category_wise(financial_years=None):
	years = normalize_financial_years(financial_years)
	if not years:
		return default_chart_response(_("Yearly Budget Plan Distributed Category Wise"))

	placeholders = ",".join(["%s"] * len(years))
	results = frappe.db.sql(
		f"""
        SELECT
            bd.budget_category,
            SUM(bd.sub_total) AS total_sub_total
        FROM `tabBudget Breakdown` bd
        JOIN `tabBudget Plan` bp ON bd.parent = bp.name
        WHERE bp.docstatus = 1 AND bp.financial_year IN ({placeholders})
        GROUP BY bd.budget_category
        ORDER BY total_sub_total DESC
    """,
		tuple(years),
		as_dict=True,
	)

	labels = [row["budget_category"] for row in results]
	datapoints = [row["total_sub_total"] for row in results]

	return {
		"labels": labels,
		"datasets": [{"name": _("Yearly Budget Plan Distributed Category Wise"), "values": datapoints}],
	}


@frappe.whitelist()
def get_budget_sub_category_wise(financial_years=None):
	years = normalize_financial_years(financial_years)
	if not years:
		return default_chart_response(_("Yearly Budget Plan Distributed Sub Category Wise"))

	placeholders = ",".join(["%s"] * len(years))
	results = frappe.db.sql(
		f"""
        SELECT
            bd.budget_sub_category,
            SUM(bd.sub_total) AS total_sub_total
        FROM `tabBudget Breakdown` bd
        JOIN `tabBudget Plan` bp ON bd.parent = bp.name
        WHERE bp.docstatus = 1 AND bp.financial_year IN ({placeholders})
        GROUP BY bd.budget_sub_category
        ORDER BY total_sub_total DESC
    """,
		tuple(years),
		as_dict=True,
	)

	labels = [row["budget_sub_category"] for row in results]
	datapoints = [row["total_sub_total"] for row in results]

	return {
		"labels": labels,
		"datasets": [{"name": _("Yearly Budget Plan Distributed Sub Category Wise"), "values": datapoints}],
	}


@frappe.whitelist()
def get_budget_level_utilisation(financial_years=None):
	years = normalize_financial_years(financial_years)
	if not years:
		return default_chart_response(_("Yearly Budget Plan Utilisation"))

	placeholders = ",".join(["%s"] * len(years))
	results = frappe.db.sql(
		f"""
        SELECT
            bp.financial_year,
            SUM(bp.yearly_budget) AS yearly_budget,
            COALESCE(SUM(ei.utilised_amount), 0) AS total_utilised_amount
        FROM `tabBudget Plan` bp
        LEFT JOIN `tabExpense Item` ei ON ei.budget_plan = bp.name
        WHERE bp.docstatus = 1 AND bp.financial_year IN ({placeholders})
        GROUP BY bp.financial_year
        ORDER BY bp.financial_year
    """,
		tuple(years),
		as_dict=True,
	)

	labels = [row["financial_year"] for row in results]
	yearly_budget_values = [row["yearly_budget"] for row in results]
	utilised_amount_values = [row["total_utilised_amount"] for row in results]

	return {
		"labels": labels,
		"datasets": [
			{"name": _("Planned Budget"), "values": yearly_budget_values},
			{"name": _("Utilised Budget"), "values": utilised_amount_values},
		],
	}


@frappe.whitelist()
def get_budget_category_wise_utilisation(financial_years=None):
	years = normalize_financial_years(financial_years)
	if not years:
		return default_chart_response(_("Budget Category Wise Utilisation"))

	placeholders = ",".join(["%s"] * len(years))

	result = frappe.db.sql(
		f"""
    SELECT
    ei.category,
    SUM(ei.utilised_amount) AS total_utilized_amount,
    (
        SELECT SUM(bb.sub_total)
        FROM `tabBudget Breakdown` bb
        WHERE bb.budget_category = ei.category
          AND bb.parent = ei.budget_plan
    ) AS total_allocated_amount
    FROM `tabExpense Item` ei
    JOIN `tabBudget Plan` bp ON ei.budget_plan = bp.name
    WHERE bp.docstatus = 1
    AND ei.docstatus = 1
    AND bp.financial_year IN ({placeholders})
    GROUP BY ei.category
    ORDER BY total_utilized_amount DESC
    """,
		tuple(years),
		as_dict=True,
	)

	labels = [row["category"] for row in result]
	allocated = [
		row["total_allocated_amount"] if row["total_allocated_amount"] is not None else 0 for row in result
	]
	utilised = [
		row["total_utilized_amount"] if row["total_utilized_amount"] is not None else 0 for row in result
	]

	return {
		"labels": labels,
		"datasets": [
			{"name": _("Allocated Budget"), "values": allocated},
			{"name": _("Utilised Budget"), "values": utilised},
		],
	}


def default_chart_response(name):
	return {"labels": [], "datasets": [{"name": name, "values": []}]}

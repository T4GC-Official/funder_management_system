import frappe
from frappe import _
import json

dashboard_logger = frappe.logger("dashboard", allow_site=True, file_count=10)


def normalize_financial_years(financial_years):
    """Helper function to parse and normalize financial_years input."""
    if not financial_years:
        return []

    if isinstance(financial_years, str):
        try:
            parsed = json.loads(financial_years)
            return parsed if isinstance(parsed, list) else [parsed]
        except json.JSONDecodeError:
            return [financial_years]

    if isinstance(financial_years, list):
        return financial_years

    return []


@frappe.whitelist()
def get_number_cards(financial_years=None):
    """Returns summary cards for the dashboard."""
    dashboard_logger.info("Fetching number cards")
    cards = [
        get_total_leads(financial_years),
        get_conversion_rate_by_fy(financial_years),
        get_churn_rate_fy(financial_years),
    ]

    # Ensure each card has a label and fieldtype
    for card in cards:
        card.setdefault("label", _("Value"))
        card.setdefault("fieldtype", "Data")

    return cards


@frappe.whitelist()
def get_total_leads(financial_years=None):
    """Returns the total number of unique Organisation Leads for the given financial years."""
    years = normalize_financial_years(financial_years)
    dashboard_logger.info(f"[Total Leads] Normalized Financial Years: {years}")

    if not years:
        dashboard_logger.warning("[Total Leads] No financial years provided or normalization failed.")
        return {
            "value": 0,
            "label": _("Total Leads"),
            "fieldtype": "Int"
        }

    try:
        total_leads = frappe.db.count("Organisation Lead", {
            "financial_year_of_reachout": ["in", years]
        })
        dashboard_logger.info(f"[Total Leads] Found {total_leads} leads for years: {years}")
    except Exception as e:
        dashboard_logger.error(f"[Total Leads] DB count failed: {frappe.get_traceback()}")
        return {
            "value": 0,
            "label": _("Total Leads"),
            "fieldtype": "Int"
        }

    return {
        "value": total_leads,
        "label": _("Total Leads"),
        "fieldtype": "Int"
    }
     


@frappe.whitelist()
def get_conversion_rate_by_fy(financial_years=None):
    """Returns conversion rate as a percent card."""
    years = normalize_financial_years(financial_years)

    if not years:
        return percent_card_response(_("Conversion Rate"), 0)

    placeholders = ','.join(['%s'] * len(years))
    total = frappe.db.sql(f"""
        SELECT COUNT(DISTINCT name)
        FROM `tabOrganisation Lead`
        WHERE financial_year_of_reachout IN ({placeholders})
    """, tuple(years))[0][0]

    confirmed = frappe.db.sql(f"""
        SELECT COUNT(DISTINCT name)
        FROM `tabOrganisation Lead`
        WHERE financial_year_of_reachout IN ({placeholders})
        AND lead_stage = 'Confirmed Lead'
    """, tuple(years))[0][0]

    rate = (confirmed / total * 100) if total else 0
    return percent_card_response(_("Conversion Rate"), rate)


@frappe.whitelist()
def get_churn_rate_fy(financial_years=None):
    """Returns churn rate as a percent card."""
    years = normalize_financial_years(financial_years)

    if not years:
        return percent_card_response(_("Churn Rate"), 0)

    placeholders = ','.join(['%s'] * len(years))
    total = frappe.db.sql(f"""
        SELECT COUNT(DISTINCT name)
        FROM `tabOrganisation Lead`
        WHERE financial_year_of_reachout IN ({placeholders})
    """, tuple(years))[0][0]

    churned = frappe.db.sql(f"""
        SELECT COUNT(DISTINCT name)
        FROM `tabOrganisation Lead`
        WHERE financial_year_of_reachout IN ({placeholders})
        AND lead_stage IN ('Cold Lead', 'Dropped Lead')
    """, tuple(years))[0][0]

    churn_rate = (churned / total * 100) if total else 0
    return percent_card_response(_("Churn Rate"), churn_rate)


@frappe.whitelist()
def get_leads_by_category(financial_years=None):
    """Returns leads grouped by category for charting."""
    return grouped_chart_response(
        table="`tabOrganisation Lead`",
        group_by="lead_category",
        years=normalize_financial_years(financial_years),
        label=_("Leads by Category")
    )


@frappe.whitelist()
def get_leads_by_lead_stages(financial_years=None):
    """Returns leads grouped by lead stage."""
    return grouped_chart_response(
        table="`tabOrganisation Lead`",
        group_by="lead_stage",
        years=normalize_financial_years(financial_years),
        label=_("Leads by Lead Stages")
    )


@frappe.whitelist()
def get_leads_by_thematic_area(financial_years=None):
    """Returns leads grouped by thematic area."""
    years = normalize_financial_years(financial_years)
    if not years:
        return default_chart_response(_("Leads by Thematic Area"))

    placeholders = ','.join(['%s'] * len(years))
    results = frappe.db.sql(f"""
        SELECT child.thematic_area, COUNT(DISTINCT child.parent) AS count
        FROM `tabThematic Area Child` child
        JOIN `tabOrganisation Lead` parent_doc ON child.parent = parent_doc.name
        WHERE parent_doc.financial_year_of_reachout IN ({placeholders})
        GROUP BY child.thematic_area
    """, tuple(years), as_dict=True)

    labels = [row["thematic_area"] for row in results]
    datapoints = [row["count"] for row in results]

    return {
        "labels": labels,
        "datasets": [
            {
                "name": _("Leads by Thematic Area"),
                "values": datapoints
            }
        ]
    }


@frappe.whitelist()
def get_leads_by_sources_of_connection(financial_years=None):
    """Returns leads grouped by sources of connection."""
    years = normalize_financial_years(financial_years)
    if not years:
        return default_chart_response(_("Leads by Sources of Connection"))

    placeholders = ','.join(['%s'] * len(years))
    results = frappe.db.sql(f"""
        SELECT child.source_of_connection, COUNT(DISTINCT child.parent) AS count
        FROM `tabSource of Connection Child` child
        JOIN `tabOrganisation Lead` parent_doc ON child.parent = parent_doc.name
        WHERE parent_doc.financial_year_of_reachout IN ({placeholders})
        GROUP BY child.source_of_connection
    """, tuple(years), as_dict=True)

    labels = [row["source_of_connection"] for row in results]
    datapoints = [row["count"] for row in results]

    return {
        "labels": labels,
        "datasets": [
            {
                "name": _("Leads by Sources of Connection"),
                "values": datapoints
            }
        ]
    }


# ---------- Helper Responses ---------- #

def percent_card_response(label, value):
    return {
        "label": label,
        "value": f"{value:.2f}",
        "fieldtype": "Percent"
    }


def default_chart_response(name):
    return {
        "labels": [],
        "datasets": [
            {
                "name": name,
                "values": []
            }
        ]
    }


def grouped_chart_response(table, group_by, years, label):
    if not years:
        return default_chart_response(label)

    placeholders = ','.join(['%s'] * len(years))
    results = frappe.db.sql(f"""
        SELECT {group_by}, COUNT(DISTINCT name) AS count
        FROM {table}
        WHERE financial_year_of_reachout IN ({placeholders})
        GROUP BY {group_by}
    """, tuple(years), as_dict=True)

    labels = [row[group_by] for row in results]
    datapoints = [row["count"] for row in results]

    return {
        "labels": labels,
        "datasets": [
            {
                "name": label,
                "values": datapoints
            }
        ]
    }

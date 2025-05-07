frappe.provide("frappe.dashboards.chart_sources");
frappe.dashboards.chart_sources["Top Donors"] = {
    method: "funder_management_system.funder_management_system.dashboard_chart_source.top_donors.top_donors.get",
};
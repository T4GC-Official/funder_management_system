frappe.provide("frappe.dashboards.chart_sources");

frappe.dashboards.chart_sources["Sources of Connection"] = {
    method: "funder_management_system.donor_acquisition_management.dashboard_chart_source.sources_of_connection.sources_of_connection.get",
}
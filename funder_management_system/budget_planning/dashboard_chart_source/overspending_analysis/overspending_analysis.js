frappe.provide("frappe.dashboards.chart_sources");

frappe.dashboards.chart_sources["Overspending Analysis"] = {
    method: "funder_management_system.budget_planning.dashboard_chart_source.overspending_analysis.overspending_analysis.get",
    filters: [
        {
            fieldname: "budget_plan",
            label: __("Budget Plan"),
            fieldtype: "Link",
            options: "Budget Plan",  // Link to the Budget Plan doctype
            default: null,  // Default to no filter
            get_query: function() {
                return {
                    filters: {
                        docstatus: 1  // Only show submitted Budget Plans
                    }
                };
            }
        }
    ]
};

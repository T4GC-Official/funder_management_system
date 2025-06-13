frappe.provide("frappe.dashboards.chart_sources");

frappe.dashboards.chart_sources["Sub Category Wise"] = {
    method: "funder_management_system.budget_planning.dashboard_chart_source.sub_category_wise.sub_category_wise.get",
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

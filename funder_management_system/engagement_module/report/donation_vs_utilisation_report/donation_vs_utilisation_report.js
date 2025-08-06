// Copyright (c) 2025, Tech4Good Community and contributors
// For license information, please see license.txt

frappe.query_reports["Donation vs Utilisation Report"] = {
	filters: [
		// {
		// 	"fieldname": "my_filter",
		// 	"label": __("My Filter"),
		// 	"fieldtype": "Data",
		// 	"reqd": 1,
		// },
	],
	onload: function(report) {
        report.page.add_inner_button(__('Go to Main Workspace'), function() {
			frappe.set_route('app', 'main-workspace');
        });
		report.page.add_inner_button(__('Open Budget Plan Report'), function() {
           frappe.set_route('query-report', 'Budget Plan Report');
        }, __('Reports'));
		report.page.add_inner_button(__('Open Budget vs Utilisation Report'), function() {
           frappe.set_route('query-report', 'Budget vs Utilisation Report');
        }, __('Reports'));
    }
};

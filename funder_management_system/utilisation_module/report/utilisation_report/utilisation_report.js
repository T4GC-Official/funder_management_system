// Copyright (c) 2025, Tech4Good Community and contributors
// For license information, please see license.txt

frappe.query_reports["Utilisation Report"] = {
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
            window.location.href = "/app/main-workspace";
        });
		report.page.add_inner_button(__('Open Budget Plan Report'), function() {
            window.location.href = "/app/query-report/Report%20Budget%20Plan";
        }, __('Reports'));
		report.page.add_inner_button(__('Open Donor Summary Report'), function() {
            window.location.href = "/app/query-report/Donor%20Summary%20Report";
        }, __('Reports'));
		
    }
};

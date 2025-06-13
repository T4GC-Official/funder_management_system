frappe.pages['fms-dashboard'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Test One',
		single_column: true
	});
frappe.call({
	method: "frappe.client.get_list",
	args: {
		doctype: "Financial Year",
		fields: ["name"]
	},
	callback: function(response) {
		if(response.message) {
			let financialYearSelect = $('<select class="form-control"></select>');
			response.message.forEach(function(fy) {
				financialYearSelect.append($('<option></option>').val(fy.name).text(fy.name));
			});
			page.main.append("<div class='flex gap-2'><NumberChart :config=\"{title: 'Total Sales', value: 123456, prefix: '$', delta: 10, deltaSuffix: '% MoM', negativeIsBetter: false}\" /><NumberChart :config=\"{title: 'Total Expenses', value: 5682, prefix: '$', delta: -2, deltaSuffix: '% MoM', negativeIsBetter: true}\" /><NumberChart :config=\"{title: 'Total Profit', value: 117774, prefix: '$', delta: 8, deltaSuffix: '% MoM', negativeIsBetter: false}\" /></div>");
		}
	}
});

}

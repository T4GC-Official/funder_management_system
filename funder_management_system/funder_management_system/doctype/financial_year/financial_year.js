// Copyright (c) 2025, Tech4Good Community and contributors
// For license information, please see license.txt

frappe.ui.form.on("Financial Year", {
	validate: function(frm) {
        const value = frm.doc.financial_year
        const pattern = /^2\d{3}-\d{2}$/;

        if (!value || !pattern.test(value)){
            frappe.msgprint({
                title: 'Invalid Financial Year',
                message: 'Financial Year must be in format YYYY-YY',
                indicator: 'red'
            });
            frappe.validated = false;
        }

	},
});


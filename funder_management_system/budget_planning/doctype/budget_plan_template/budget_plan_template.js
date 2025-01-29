// Copyright (c) 2025, Tech4Good Community and contributors
// For license information, please see license.txt


frappe.ui.form.on("Budget Plan Template", {
    refresh: function(frm) {
        frm.fields_dict['budget_detail'].grid.get_field('budget_sub_category').get_query = function(doc, cdt, cdn) {
            let row = locals[cdt][cdn];
            if (row.budget_category) {
                return {
                    filters: {
                        budget_category: row.budget_category
                    }
                };
            }
            return {};
        };
    }
});

frappe.ui.form.on("Budget Breakdown", {
    budget_sub_category: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.budget_category && row.budget_sub_category) {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Budget Sub-Category",
                    filters: {
                        budget_category: row.budget_category,
                        name: row.budget_sub_category
                    },
                    fields: ["name"]
                },
                callback: function(r) {
                    if (!r.message || r.message.length === 0) {
                        frappe.msgprint(__('The selected sub-category is not valid for the chosen category.'));
                        row.budget_sub_category = "";
                        frm.refresh_field('budget_breakdown');
                    }
                }
            });
        }
    }
});


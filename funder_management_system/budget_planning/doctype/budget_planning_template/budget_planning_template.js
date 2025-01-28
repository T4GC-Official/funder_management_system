// Copyright (c) 2025, Tech4Good Community and contributors
// For license information, please see license.txt

frappe.ui.form.on("Budget Planning Template", {
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

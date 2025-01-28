// Copyright (c) 2025, Tech4Good Community and contributors
// For license information, please see license.txt

frappe.ui.form.on("Budget Planning", {
    budget_planning_template: function (frm) {
        if (frm.doc.budget_planning_template) {
            frappe.call({
                method: "funder_management_system.budget_planning.doctype.budget_planning.budget_planning.get_budget_detail",
                args: {
                    template_name: frm.doc.budget_planning_template,
                },
                callback: function (r) {
                    if (r.message) {
                        frm.clear_table("budget_breakdown");
                        console.log(r.message);
                        r.message.forEach((row) => {
                            let child_row = frm.add_child("budget_breakdown");
                            child_row.budget_category = row.budget_category;
                            child_row.budget_sub_category = row.budget_sub_category;
                            child_row.quarter_1_budget = row.quarter_1_budget;
                            child_row.quarter_2_budget = row.quarter_2_budget;
                            child_row.quarter_3_budget = row.quarter_3_budget;
                            child_row.quarter_4_budget = row.quarter_4_budget;
                            child_row.sub_total = row.sub_total;
                        });
                        frm.refresh_field("budget_breakdown");
                    }
                },
            });
        }
    },
    refresh: function(frm) {
        frm.fields_dict['budget_breakdown'].grid.get_field('budget_sub_category').get_query = function(doc, cdt, cdn) {
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

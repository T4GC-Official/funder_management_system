frappe.ui.form.on("Budget Plan", {
    refresh: function(frm) {
        // Ensure child table exists before applying styles
        if (frm.fields_dict['budget_breakdown'] && frm.fields_dict['budget_breakdown'].grid && frm.fields_dict['budget_breakdown'].grid.wrapper) {
            frm.fields_dict['budget_breakdown'].grid.wrapper.find('.grid-heading-row').css("white-space", "normal");
            frm.fields_dict['budget_breakdown'].grid.wrapper.css("overflow-x", "auto");
        }

        // Set filter for budget_sub_category dynamically
        if (frm.fields_dict['budget_breakdown'] && frm.fields_dict['budget_breakdown'].grid) {
            let field = frm.fields_dict['budget_breakdown'].grid.get_field('budget_sub_category');
            if (field) {
                field.get_query = function(doc, cdt, cdn) {
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
        }
    },

    budget_plan_template: function(frm) {
        if (frm.doc.budget_plan_template) {
            frappe.call({
                method: "funder_management_system.budget_planning.doctype.budget_plan.budget_plan.get_budget_detail",
                args: {
                    template_name: frm.doc.budget_plan_template,
                },
                callback: function(r) {
                    if (r.message && Array.isArray(r.message)) {
                        frm.clear_table("budget_breakdown");
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
                    } else {
                        frappe.msgprint(__('No budget details found for the selected template.'));
                    }
                },
                error: function() {
                    frappe.msgprint(__('Failed to fetch budget details.'));
                }
            });
        }
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
                    if (r.exc) {
                        frappe.msgprint(__('Error fetching sub-category data.'));
                        return;
                    }
                    if (!r.message || r.message.length === 0) {
                        frappe.msgprint(__('The selected sub-category is not valid for the chosen category.'));
                        row.budget_sub_category = "";  // Reset invalid subcategory
                        frm.refresh_field('budget_breakdown');
                    }
                },
                error: function() {
                    frappe.msgprint(__('Failed to validate the budget sub-category.'));
                }
            });
        }
    }
});

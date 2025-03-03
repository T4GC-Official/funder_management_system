frappe.ui.form.on("Budget Plan", {
    refresh: function (frm) {
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
        onload: function (frm) {
            let grid = frm.fields_dict["budget_breakdown"].grid;
            // Override only for this specific grid
            grid.setup_visible_columns = function () {
                let column_count = 7;  // Total number of columns
                let column_width = Math.floor(14 / column_count); // Distribute width equally
    
                this.visible_columns = [];
                let fields = this.editable_fields || this.docfields;
                let total_colsize = 0;
    
                for (var ci in fields) {
                    var df = this.fields_map[fields[ci].fieldname];
    
                    if (
                        df &&
                        !df.hidden &&
                        (this.editable_fields || df.in_list_view) &&
                        ((this.frm && this.frm.get_perm(df.permlevel, "read")) || !this.frm) &&
                        !frappe.model.layout_fields.includes(df.fieldtype)
                    ) {
                        df.colsize = column_width;
                        total_colsize += df.colsize;
                        this.visible_columns.push([df, df.colsize]);
                    }
                }
    
            };
    
            // Refresh grid to apply new column sizes
            grid.refresh();
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

                        // Adjust widths after data is loaded
                        setTimeout(() => {
                            adjustTableWidths();
                        }, 200);
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



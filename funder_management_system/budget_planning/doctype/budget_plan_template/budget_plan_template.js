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
    },
    onload: function (frm) {
        let grid = frm.fields_dict["budget_detail"].grid;

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


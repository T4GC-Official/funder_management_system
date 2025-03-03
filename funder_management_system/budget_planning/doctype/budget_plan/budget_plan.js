frappe.ui.form.on("Budget Plan", {
        // setup: function (frm) {
        //     console.log("setup");
        // frm.set_query("financial_year", function () {
        //     console.log("financial_year");
        //         return {limit_page_length: 1000 }}
        // )},
            //         let current_year = new Date().getFullYear(); // Get current year
        //         let start_year = current_year - 5;  // Previous 5 years
        //         let end_year = current_year + 3;  // Next 3 years
    
        //         let start_fy = start_year + "-" + (start_year + 1).toString().slice(-2); // "2020-21"
        //         let end_fy = end_year + "-" + (end_year + 1).toString().slice(-2); // "2030-31"
    
        //         return {
        //             filters: [
        //                 ["financial_year", "between", [start_fy, end_fy]]
        //             ],
        //             order_by: "financial_year ASC"
        //         };
        //     });
        // },
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
    
    refresh: function(frm) {
        setTimeout(() => {
            let grid_wrapper = frm.fields_dict['budget_breakdown'].grid.wrapper;

            // Function to dynamically set column widths based on the row with the most content
            function adjustTableWidths() {
                const table = grid_wrapper.find("table");
                if (!table.length) return;

                const headerCells = table.find("thead th");
                const rows = table.find("tbody tr");
                if (!rows.length || !headerCells.length) return;

                // Find the row with the most content (widest)
                let widestRow = null;
                let maxWidth = 0;

                rows.each(function() {
                    let rowWidth = $(this).outerWidth();
                    if (rowWidth > maxWidth) {
                        maxWidth = rowWidth;
                        widestRow = $(this);
                    }
                });

                if (!widestRow) return;

                // Apply column widths from the widest row
                const widestRowCells = widestRow.find("td");
                widestRowCells.each(function(index) {
                    let cellWidth = $(this).outerWidth();
                    if (headerCells[index]) {
                        $(headerCells[index]).css("width", cellWidth + "px");
                    }
                    rows.each(function() {
                        $(this).find("td").eq(index).css("width", cellWidth + "px");
                    });
                });
            }

            // Adjust after rendering and on window resize
            setTimeout(adjustTableWidths, 100);
            $(window).on("resize", adjustTableWidths);
            frm.fields_dict['budget_breakdown'].grid.wrapper.on("scroll", adjustTableWidths);
        }, 500);

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
                        row.budget_sub_category = "";
                        frm.refresh_field("budget_breakdown");
                    }
                }
            });
        }
    }
});

let is_updating_totals = false;

frappe.ui.form.on("Budget Plan", {
    after_save(frm) {
        is_updating_totals = false;
    },

    onload(frm) {
        // Inject explicit Grid CSS to ensure the grid does not collapse
        // This overrides the v16 max-width: 50% issue
        if (!document.getElementById('budget-breakdown-grid-style')) {
            const style = document.createElement('style');
            style.id = 'budget-breakdown-grid-style';
            style.innerHTML = `
                /* 
                   Force full width on the specific form column that houses the table.
                   Frappe places tables in a .col-sm-6 or .col-sm-12 natively, we force it to expand.
                */
                .form-column:has([data-fieldname="budget_breakdown"]) {
                    max-width: 100% !important;
                    width: 100% !important;
                    flex: 0 0 100% !important;
                }
                
                /* Force full width on container elements */
                [data-fieldname="budget_breakdown"],
                [data-fieldname="budget_breakdown"].frappe-control,
                [data-fieldname="budget_breakdown"].frappe-control.input-max-width,
                [data-fieldname="budget_breakdown"].frappe-control .form-group,
                [data-fieldname="budget_breakdown"] .form-grid-container,
                [data-fieldname="budget_breakdown"] .form-grid,
                [data-fieldname="budget_breakdown"] .grid-heading-row,
                [data-fieldname="budget_breakdown"] .rows,
                [data-fieldname="budget_breakdown"] .grid-body {
                    max-width: 100% !important;
                    width: 100% !important;
                }
                
                /* Ensure columns distribute available width equally instead of fixed widths */
                [data-fieldname="budget_breakdown"] .data-row .col.grid-static-col,
                [data-fieldname="budget_breakdown"] .grid-heading-row .col.grid-static-col {
                    flex: 1 1 0% !important;
                    max-width: none !important;
                    width: auto !important;
                    min-width: 0 !important;
                }
                
                /* Prevent rows from wrapping incorrectly */
                [data-fieldname="budget_breakdown"] .data-row.row {
                    flex-wrap: nowrap !important;
                }
                
                /* Keep Checkbox and Row Settings Button tight */
                [data-fieldname="budget_breakdown"] .row-check,
                [data-fieldname="budget_breakdown"] .data-row > .col:last-child {
                    flex: 0 0 auto !important;
                    max-width: 36px !important;
                }
                
                /* Hide row index natively */
                [data-fieldname="budget_breakdown"] .row-index {
                    display: none !important;
                }
            `;
            document.head.appendChild(style);
        }

        const grid = frm.fields_dict["budget_breakdown"]?.grid;
        if (grid) {
            grid.setup_visible_columns = function () {
                this.visible_columns = [];
                const fields = this.editable_fields || this.docfields;
                for (let f of fields) {
                    const df = this.fields_map[f.fieldname];
                    if (
                        df &&
                        !df.hidden &&
                        (this.editable_fields || df.in_list_view) &&
                        ((this.frm && this.frm.get_perm(df.permlevel, "read")) || !this.frm) &&
                        !frappe.model.layout_fields.includes(df.fieldtype)
                    ) {
                        // Using colsize 1 ensures total_colsize < 10, preventing native "column-limit-reached" breakage
                        df.colsize = 1; 
                        this.visible_columns.push([df, df.colsize]);
                    }
                }
            };
            grid.visible_columns = null;
            grid.refresh();
        }
    },

    refresh(frm) {

        // === Apply filter on Sub-Category field based on Category ===
        if (frm.fields_dict['budget_breakdown']?.grid) {
            const field = frm.fields_dict['budget_breakdown'].grid.get_field('budget_sub_category');
            if (field) {
                field.get_query = function (doc, cdt, cdn) {
                    const row = locals[cdt][cdn];
                    return row.budget_category
                        ? { filters: { budget_category: row.budget_category } }
                        : {};
                };
            }
        }

        // Only update totals when form first loads, not after auto-save
        if (!is_updating_totals) update_totals(frm);
    },

    budget_plan_template(frm) {
        if (!frm.doc.budget_plan_template) return;
        frappe.call({
            method: "funder_management_system.budget_planning.doctype.budget_plan.budget_plan.get_budget_detail",
            args: { template_name: frm.doc.budget_plan_template },
            callback(r) {
                if (r.message && Array.isArray(r.message)) {
                    frm.clear_table("budget_breakdown");
                    r.message.forEach(row => {
                        frm.add_child("budget_breakdown", row);
                    });
                    frm.refresh_field("budget_breakdown");
                    update_totals(frm);
                } else {
                    frappe.msgprint(__('No budget details found for the selected template.'));
                }
            },
            error() {
                frappe.msgprint(__('Failed to fetch budget details.'));
            }
        });
    }
});

// === Child Table Triggers ===
frappe.ui.form.on('Budget Breakdown', {
    quarter_1_budget(frm) { update_totals(frm); },
    quarter_2_budget(frm) { update_totals(frm); },
    quarter_3_budget(frm) { update_totals(frm); },
    quarter_4_budget(frm) { update_totals(frm); },
});

// === Function to calculate and update totals ===
function update_totals(frm) {
    if (is_updating_totals) return;
    is_updating_totals = true;

    let total_q1 = 0, total_q2 = 0, total_q3 = 0, total_q4 = 0;

    (frm.doc.budget_breakdown || []).forEach(row => {
        const q1 = row.quarter_1_budget || 0;
        const q2 = row.quarter_2_budget || 0;
        const q3 = row.quarter_3_budget || 0;
        const q4 = row.quarter_4_budget || 0;

        row.sub_total = q1 + q2 + q3 + q4;
        total_q1 += q1;
        total_q2 += q2;
        total_q3 += q3;
        total_q4 += q4;
    });

    frm.set_value({
        total_quarter_1_budget: total_q1,
        total_quarter_2_budget: total_q2,
        total_quarter_3_budget: total_q3,
        total_quarter_4_budget: total_q4,
        yearly_budget: total_q1 + total_q2 + total_q3 + total_q4
    });

    frm.refresh_fields([
        'total_quarter_1_budget',
        'total_quarter_2_budget',
        'total_quarter_3_budget',
        'total_quarter_4_budget',
        'yearly_budget'
    ]);

    is_updating_totals = false;
}

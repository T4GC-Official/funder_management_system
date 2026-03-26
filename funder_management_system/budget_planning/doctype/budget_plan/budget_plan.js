let is_updating_totals = false;

frappe.ui.form.on("Budget Plan", {
    after_save(frm) {
        is_updating_totals = false;
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
                        let child = frm.add_child("budget_breakdown", row);
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
        'budget_breakdown',
        'total_quarter_1_budget',
        'total_quarter_2_budget',
        'total_quarter_3_budget',
        'total_quarter_4_budget',
        'yearly_budget'
    ]);

    is_updating_totals = false;
}

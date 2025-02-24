frappe.ui.form.on("Expense", {
    refresh: function(frm) {
        // Ensure budget UI is added only once
        if (!frm.custom_budget_section_added) {
            render_budget_status(frm);
            frm.custom_budget_section_added = true;
        }

        // Add Submit Button in the form actions
        frm.add_custom_button("Submit Expenses", function() {
            frappe.confirm(
                "Are you sure you want to submit these expenses?",
                () => {
                    frm.save();
                    frappe.msgprint("Expenses submitted successfully.");
                }
            );
        }, "Actions");
    }
});

function render_budget_status(frm) {
    // Locate the Expense Details section
    if (!frm.fields_dict.expense_details_section) {
        console.warn("Field expense_details_section is missing in the form.");
        return;
    }

    let budget_section = $(frm.fields_dict.expense_details_section.wrapper);
    budget_section.empty(); // Clear existing content

    // Budget UI HTML
    let budget_html = `
        <div style="padding: 10px; background: #f8f9fa; border-radius: 5px; margin-top: 10px;">
            <h4 style="margin-bottom: 10px;">Budget Utilization</h4>
            <div style="display: flex; align-items: center; gap: 10px;">
                <strong>Utilization Source:</strong>
                <span>${frm.doc.utilisation_source || "Single Donor Fund"}</span>
                <strong>Total Utilized:</strong>
                <span style="font-weight: bold;">₹ ${frm.doc.total_utilised_amount || "0.00"}</span>
                <input type="range" min="0" max="100" value="0" class="expense-slider" style="width: 150px;">
                <button class="btn btn-primary btn-xs add-expense">Add Expense</button>
            </div>
        </div>
    `;

    budget_section.append(budget_html);

    // Attach Event Handlers
    budget_section.find(".add-expense").click(function() {
        frm.trigger("add_expense");
    });
}

frappe.ui.form.on("Expenditure Detail", {
    utilised_amount: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        let slider = $(`.expense-slider`);
        slider.val(row.utilised_amount);
    },

    move_expense: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        frappe.prompt(
            [
                { label: "New Category", fieldname: "new_category", fieldtype: "Link", options: "Category" },
                { label: "New Sub-Category", fieldname: "new_sub_category", fieldtype: "Data" }
            ],
            function(values) {
                frappe.model.set_value(cdt, cdn, "category", values.new_category);
                frappe.model.set_value(cdt, cdn, "sub_category", values.new_sub_category);
                frappe.msgprint("Expense moved successfully.");
            },
            "Move Expense",
            "Move"
        );
    }
});

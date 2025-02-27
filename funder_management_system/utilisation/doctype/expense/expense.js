frappe.ui.form.on("Expense", {
    refresh: function(frm) {
        if (!frm.fields_dict["expense_details_section"]) {
            return;
        }

        render_expense_entry_ui(frm);
    }
});

function render_expense_entry_ui(frm) {
    let wrapper = $(frm.fields_dict.expense_details_section.wrapper);
    wrapper.empty(); // Clear existing UI

    let expense_html = `
    <div class="frappe-control" style="padding: 15px; border: 1px solid #d1d8dd; border-radius: 5px; background: #f8f9fa;">
        <table class="table table-bordered table-hover">
            <thead>
                <tr>
                    <th>Category</th>
                    <th>Sub-Category</th>
                    <th>Donor</th>
                    <th>Grant Agreement</th>
                    <th>Tranche</th>
                    <th>Available Amount</th>
                    <th>Utilised Amount</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><div class="category"></div></td>
                    <td><div class="sub_category"></div></td>
                    <td><div class="donor"></div></td>
                    <td><div class="grant_agreement"></div></td>
                    <td><div class="tranche"></div></td>
                    <td><div class="available_amount"></div></td>
                    <td><div class="utilised_amount"></div></td>
                    <td>
                        <button class="btn btn-primary add-expense">Add Expense</button>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
`;

wrapper.append(expense_html);


    let category_control = frappe.ui.form.make_control({
        parent: wrapper.find(".category"),
        df: { fieldtype: "Link", options: "Budget Category", label: "Category" },
        only_input: true
    });
    category_control.refresh();

    let sub_category_control = frappe.ui.form.make_control({
        parent: wrapper.find(".sub_category"),
        df: { fieldtype: "Select", label: "Sub-Category", options: [] },
        only_input: true
    });
    sub_category_control.refresh();

    let donor_control = frappe.ui.form.make_control({
        parent: wrapper.find(".donor"),
        df: {
            fieldtype: "Link",
            options: "Donor",
            label: "Donor",
            onchange: function () {
                load_grant_agreements(donor_control.get_value(), grant_agreement_control);
            }
        },
        only_input: true
    });
    donor_control.refresh();

    let grant_agreement_control = frappe.ui.form.make_control({
        parent: wrapper.find(".grant_agreement"),
        df: { fieldtype: "Select", label: "Grant Agreement", options: [] },
        only_input: true
    });
    grant_agreement_control.refresh();

    let tranche_control = frappe.ui.form.make_control({
        parent: wrapper.find(".tranche"),
        df: { fieldtype: "Select", label: "Tranche", options: [] },
        only_input: true
    });
    tranche_control.refresh();

    let available_amount_control = frappe.ui.form.make_control({
        parent: wrapper.find(".available_amount"),
        df: { fieldtype: "Currency", label: "Available Amount", read_only: 1 },
        only_input: true
    });
    available_amount_control.refresh();

    let utilised_amount_control = frappe.ui.form.make_control({
        parent: wrapper.find(".utilised_amount"),
        df: { fieldtype: "Currency", label: "Utilised Amount" },
        only_input: true
    });
    utilised_amount_control.refresh();

    // Add Expense Button Click
    wrapper.find(".add-expense").click(function () {
        let category = category_control.get_value();
        let sub_category = sub_category_control.get_value();
        let donor = donor_control.get_value();
        let grant_agreement = grant_agreement_control.get_value();
        let tranche = tranche_control.get_value();
        let available_amount = available_amount_control.get_value();
        let utilised_amount = utilised_amount_control.get_value();

        if (!category || !sub_category || !donor || !grant_agreement || !tranche || !utilised_amount) {
            frappe.msgprint("Please fill all fields before adding an expense.");
            return;
        }

        frappe.call({
            method: "frappe.client.insert",
            args: {
                doc: {
                    doctype: "Expense Entry",
                    category: category,
                    sub_category: sub_category,
                    donor: donor,
                    grant_agreement: grant_agreement,
                    tranche: tranche,
                    available_amount: available_amount,
                    utilised_amount: utilised_amount
                }
            },
            callback: function (response) {
                if (!response.exc) {
                    frappe.msgprint("Expense added successfully!");
                }
            }
        });
    });

    // Load sub-categories when category is selected
    category_control.$input.on("change", function () {
        load_sub_categories(category_control.get_value(), sub_category_control);
    });

    // Load grant agreements when donor is selected
    donor_control.$input.on("change", function () {
        load_grant_agreements(donor_control.get_value(), grant_agreement_control);
    });

    // Load tranches when grant agreement is selected
    grant_agreement_control.$input.on("change", function () {
        load_tranches(grant_agreement_control.get_value(), tranche_control, available_amount_control);
    });
}

// Load sub-categories based on category selection
function load_sub_categories(category, sub_category_control) {
    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "Budget Sub-Category",
            filters: { budget_category: category },
            fields: ["name"]
        },
        callback: function (response) {
            console.log("Inside load sub category ",response);
            let sub_categories = response.message || [];
            let options = sub_categories.map(sub => sub.name);
            sub_category_control.df.options = options;
            sub_category_control.refresh();
        }
    });
}

// Load grant agreements based on donor selection
function load_grant_agreements(donor, grant_agreement_control) {
    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "Grant Agreement",
            filters: { donor: donor },
            fields: ["name"]
        },
        callback: function (response) {
            console.log("Inside GA ",response);
            let agreements = response.message || [];
            let options = agreements.map(ga => ga.name);
            grant_agreement_control.df.options = options;
            grant_agreement_control.refresh();
        }
    });
}

function load_tranches(grant_agreement, tranche_control, available_amount_control) {
    frappe.call({
        method: "frappe.client.get",
        args: { doctype: "Grant Agreement", name: grant_agreement },
        callback: function (response) {
            console.log("Inside GA Tranche ", response);
            let agreement = response.message;
            let tranches = agreement.tranche_table || []; // Ensure this matches your child table name

            // Store tranche data for reference
            let tranche_map = {};
            let options = tranches.map(tr => {
                tranche_map[tr.tranche_name] = tr.tranche_amount;
                return tr.tranche_name;
            });

            tranche_control.df.options = options;
            tranche_control.refresh();

            // Set available amount based on the first tranche
            if (tranches.length > 0) {
                available_amount_control.set_value(tranches[0].tranche_amount);
            }

            // Update available amount when tranche selection changes
            tranche_control.$input.on("change", function () {
                let selected_tranche = tranche_control.get_value();
                if (tranche_map[selected_tranche]) {
                    available_amount_control.set_value(tranche_map[selected_tranche]);
                }
            });
        }
    });
}

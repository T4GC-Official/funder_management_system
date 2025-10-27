// Copyright (c) 2025, Tech4Good Community
// For license information, please see license.txt

frappe.ui.form.on("Utilisation Record", {
    onload(frm) {
        frm.trigger("set_donor_list");
        frm.trigger("set_financial_year");
    },
    refresh: function (frm) {
        if (!frm.doc.__islocal) {
            renderExpenseButtons(frm)
            frm.trigger("check_if_child_table_is_updated");
        }

        // Restrict child table editing
        ["cannot_add_rows", "cannot_delete_rows", "cannot_delete_all_rows"].forEach(prop =>
            frm.set_df_property("utilisation_child_table", prop, true)
        );

        frm.set_df_property("grant_agreement", "only_select", 1);
    },

    check_if_child_table_is_updated(frm) {
        frappe.call({
            method: "funder_management_system.utilisation_module.doctype.utilisation_record.utilisation_record.check_if_child_table_is_updated",
            args: { document_name: frm.doc.name },
            freeze: false,
            async: false,
            callback(r) {
                if (r.message) frm.reload_doc();
            }
        });
    },
    before_save: function (frm) {
        frm.set_value('budget', null);
        frm.set_value('grant_agreement', null);
        frm.set_value('grant_tranche_name', null);
        frm.set_value("financial_year", null);
        frm.set_value("donor", null);
        frm.set_value("budget_category", null);
        frm.set_value("budget_sub_category", null);
        frm.set_value("expenditure", 0);
        frm.set_value("expense_title", null);
        frm.set_value("expense_date", null);
        frm.set_value("quarters", null);

    },

    after_save(frm) {
        frappe.call({
            method: "funder_management_system.utilisation_module.doctype.expense_item.expense_item.create_utilisation_entries",
            args: { document_name: frm.doc.name },
            freeze: true,
            async: false
        });
    },

    update_child_table(frm) {
        frm.refresh_field("utilisation_child_table");
    },

    donor(frm) {
        frm.set_query("grant_agreement", () =>
            frm.doc.donor ? { filters: { donor: frm.doc.donor } } : {}
        );
        frm.set_value("grant_agreement", null);
        frm.set_value("grant_tranche_name", null);
    },

    grant_agreement(frm) {
        const { grant_agreement, donor } = frm.doc;

        if (grant_agreement && donor) {
            frappe.db.get_doc("Grant Agreement", grant_agreement).then(grant => {
                if (grant) {
                    frm.dashboard.clear_headline();
                    renderTrancheTable(frm, grant);
                }
            });
        } else if (!donor) {
            frm.set_value("grant_agreement", null);
            frm.set_value("grant_tranche_name", null);
            frm.fields_dict.donor.set_focus();
        }

        frm.set_query("grant_tranche_name", () =>
            grant_agreement ? { filters: { parent: grant_agreement } } : {}
        );

        loadTranches(frm);
    },

    budget_category(frm) {
        frm.trigger("set_budget_sub_category");
    },

    financial_year(frm) {
        frm.trigger("set_budget_plan");
    },

    set_financial_year(frm) {
        frappe.db.get_list("Financial Year", {
            fields: ["financial_year"],
            order_by: "financial_year DESC"
        }).then(response => {
            const options = response.map(doc => doc.financial_year).join("\n");
            frm.set_df_property("financial_year", "options", options);
        });
    },

    set_budget_plan(frm) {
        frappe.db.get_list("Budget Plan", {
            fields: ["name"],
            filters: {
                financial_year: frm.doc.financial_year,
                docstatus: 1
            }
        }).then(response => {
            const options = response.map(doc => doc.name).join("\n");
            frm.set_df_property("budget", "options", options || "");
        });
    },

    set_budget_sub_category(frm) {
        frappe.db.get_list("Budget Sub-Category", {
            fields: ["budget_sub_category"],
            filters: { budget_category: frm.doc.budget_category }
        }).then(response => {
            const options = response.map(doc => doc.budget_sub_category).join("\n");
            frm.set_df_property("budget_sub_category", "options", options || "");
        });
    },

    set_donor_list(frm) {
        frappe.db.get_list("Donor", {
            fields: ["donor_name"],
            order_by: "donor_name"
        }).then(response => {
            const options = response.map(doc => doc.donor_name).join("\n");
            frm.set_df_property("donor", "options", options || "");
        });
    },

    budget(frm) {
        if (!frm.doc.budget) {
            frm.set_query("budget", () => ({
                filters: { financial_year: frm.doc.financial_year }
            }));

            frm.set_value("budget_category", null);
            frm.set_df_property("budget_category", "options", "");
            return;
        }

        frappe.db.get_doc("Budget Plan", frm.doc.budget).then(budget => {
            if (budget.financial_year !== frm.doc.financial_year) {
                frappe.show_alert(__("Selected Budget does not match the selected Financial Year."), 5);
                frm.set_value("budget", null);
                return;
            }

            const categories = [...new Set(budget.budget_breakdown.map(i => i.budget_category))];
            frm.set_df_property("budget_category", "options", categories.join("\n"));
            frm.dashboard.clear_headline();
            renderBudgetInfo(frm, budget);
        });
    },

    after_workflow_action(frm) {
        frm.reload_doc();
    },

    create_expense_record(frm) {
        const requiredFields = [
            "financial_year", "budget", "donor", "grant_agreement", "grant_tranche_name",
            "quarters", "budget_category", "budget_sub_category", "expenditure"
        ];

        const missingField = requiredFields.find(f => !frm.doc[f]);
        if (missingField) {
            frm.fields_dict[missingField]?.set_focus();
            frappe.throw("Please fill in all the required fields.");
            return;
        }

        const data = {
            financial_year: frm.doc.financial_year,
            budget_plan: frm.doc.budget,
            quarters: frm.doc.quarters,
            donor: frm.doc.donor,
            expense_title: frm.doc.expense_title,
            expense_date: frm.doc.expense_date,
            grant_agreement: frm.doc.grant_agreement,
            grant_agreement_tranche: frm.doc.grant_tranche_name,
            category: frm.doc.budget_category,
            sub_category: frm.doc.budget_sub_category,
            utilised_amount: frm.doc.expenditure
        };

        frm.add_child("utilisation_child_table", data);
        frm.refresh_field("utilisation_child_table");

        // Clear form fields after adding
        ["grant_tranche_name", "budget_category", "budget_sub_category", "expenditure"]
            .forEach(f => frm.set_value(f, null));
    }
});

// --------------------------
// Helper Functions
// --------------------------

function loadTranches(frm) {
    if (!frm.doc.grant_agreement) {
        frm.set_value("grant_tranche_name", null);
        frm.tranche_map = {};
        return;
    }

    frappe.call({
        method: "frappe.client.get",
        args: { doctype: "Grant Agreement", name: frm.doc.grant_agreement },
        callback({ message }) {
            if (!message) return;

            const tranches = message.tranche_table || [];
            frm.tranche_map = {};

            const options = tranches.map(tr => {
                frm.tranche_map[tr.tranche_name] = tr.tranche_amount;
                return tr.tranche_name;
            });

            if (frm.fields_dict.grant_tranche_name) {
                frm.fields_dict.grant_tranche_name.df.options = options.join("\n");
                frm.fields_dict.grant_tranche_name.refresh();
            }

            if (tranches.length) {
                frm.set_value("grant_tranche_name", tranches[0].tranche_name);
            }
        }
    });
}

function getCurrencySymbol(callback) {
    frappe.call({
        method: "frappe.client.get_value",
        args: {
            doctype: "Currency",
            fieldname: "symbol",
            filters: { name: frappe.defaults.get_default("currency") }
        },
        callback({ message }) {
            const symbol = message?.symbol || "$";
            callback(symbol);
        }
    });
}

function formatCurrency(amount, symbol) {
    const locale = frappe.defaults.get_default("currency") === "INR" ? "en-IN" : "en-US";
    const value = amount ? amount.toLocaleString(locale, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : "0.00";
    return `${symbol} ${value}`;
}

function renderBudgetInfo(frm, budget) {
    getCurrencySymbol(symbol => {
        const html = `
            <div class="frappe-control mt-2 w-100">
                <label class="control-label fw-bold">Budget Details</label>
                <div class="control-value">
                    <table class="table table-bordered table-hover w-100">
                        <thead class="table-light">
                            <tr>
                                <th>Budget</th><th>FY</th>
                                <th>1st Quarter</th><th>2nd Quarter</th>
                                <th>3rd Quarter</th><th>4th Quarter</th>
                                <th>Total Budget</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>${budget.name}</td>
                                <td>${budget.financial_year}</td>
                                <td>${formatCurrency(budget.total_quarter_1_budget, symbol)}</td>
                                <td>${formatCurrency(budget.total_quarter_2_budget, symbol)}</td>
                                <td>${formatCurrency(budget.total_quarter_3_budget, symbol)}</td>
                                <td>${formatCurrency(budget.total_quarter_4_budget, symbol)}</td>
                                <td>${formatCurrency(budget.yearly_budget, symbol)}</td>
                            </tr>
                        </tbody>
                        <tfoot>
                            <tr>
                                <td colspan="7" class="text-start fst-italic">
                                    Note: All budget values are displayed in ${symbol}. FY = Financial Year
                                </td>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            </div>
        `;

        frm.fields_dict.budget_table_view_section?.$wrapper.html(html);
    });
}

function renderTrancheTable(frm, grant) {
    const field = frm.fields_dict.grant_table_view_section;
    if (!field) return console.error("grant_table_view_section not found.");

    const tranches = grant.tranche_table || [];
    if (!tranches.length) return console.warn("No tranche data available.");

    getCurrencySymbol(symbol => {
        let html = `
            <div class="frappe-control mt-2 w-100">
                <label class="control-label fw-bold">Tranche Details</label>
                <div class="control-value">
                    <table class="table table-bordered table-hover w-100 text-center">
                        <thead class="table-light">
                            <tr>
                                <th>Tranche Info</th>
                                ${tranches.map(tr => `<th>${tr.tranche_name}</th>`).join("")}
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td><b>Amount</b></td>${tranches.map(tr => `<td>${formatCurrency(tr.tranche_amount, symbol)}</td>`).join("")}</tr>
                            <tr><td><b>Status</b></td>${tranches.map(tr => `<td>${tr.tranche_status}</td>`).join("")}</tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;

        field.$wrapper.html(html);
    });
}

function renderExpenseButtons(frm) {
    frappe.call({
        method: "funder_management_system.utilisation_module.doctype.utilisation_record.utilisation_record.count_expense_items",
        args: { urn: frm.doc.name },
        callback({ message }) {
            const counts = message || {};
            const buttons = [
                { label: "Submitted Expense Items", status: 1, color: "btn-primary", count: counts[1] },
                { label: "Cancelled Expense Items", status: 2, color: "btn-danger", count: counts[2] }
            ];

            buttons.forEach(cfg => {
                const btn = frm.add_custom_button(`${__(cfg.label)} (${cfg.count})`, () =>
                    frappe.set_route("List", "Expense Item", { urn: frm.doc.name, docstatus: cfg.status })
                );
                $(btn).removeClass("btn-default").addClass(cfg.color);
            });
        }
    });
}

// Real-time reload handler
frappe.realtime.on("reload_utilisation", data => {
    if (cur_frm && cur_frm.doc.name === data.utilisation) cur_frm.reload_doc();
});

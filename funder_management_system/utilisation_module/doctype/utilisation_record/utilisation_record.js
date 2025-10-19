// Copyright (c) 2025, Tech4Good Community and contributors
// For license information, please see license.txt

frappe.ui.form.on("Utilisation Record", {

    onload: function (frm) {
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
    check_if_child_table_is_updated: function (frm) {
        
        frappe.call({
            method: "funder_management_system.utilisation_module.doctype.utilisation_record.utilisation_record.check_if_child_table_is_updated",

            args: {
                document_name: frm.doc.name
            },
            freeze: false,
            async: true,
            callback: function (r) {
                if (r.message) {
                    frm.reload_doc();
                }
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
        frm.set_value("expenditure", null);
        frm.set_value("expense_title", null);
        frm.set_value("expense_date", null);
        frm.set_value("quarters", null);

    },

    after_save: function (frm) {
        frappe.call({
            method: "funder_management_system.utilisation_module.doctype.expense_item.expense_item.create_utilisation_entries",
            args: {
                document_name: frm.doc.name
            },
            freeze: true,
            async: false,
        });
    },

    update_child_table: function (frm) {
        frm.refresh_field('utilisation_child_table');
    },


    donor: function (frm) {
        frm.set_query('grant_agreement', () => {
            return frm.doc.donor ? { filters: { donor: frm.doc.donor } } : {};
        });
        frm.set_value('grant_agreement', null);
        frm.set_value('grant_tranche_name', null);
    },

    grant_agreement: function (frm) {
        if (frm.doc.grant_agreement && frm.doc.donor) {
            frappe.db.get_doc("Grant Agreement", frm.doc.grant_agreement).then(grant => {
                if (grant) {
                    frm.dashboard.clear_headline();
                    render_tranche_table(frm, grant);
                }
            });
        }
        if (!frm.doc.donor) {
            frm.set_value('grant_agreement', null);
            frm.set_value('grant_tranche_name', null);
            frm.fields_dict.donor.set_focus();
        }
        frm.set_query('grant_tranche_name', () => {
            return frm.doc.grant_agreement ? { filters: { parent: frm.doc.grant_agreement } } : {};
        });
        load_tranches(frm);
    },



    budget_category: function (frm) {
        frm.trigger("set_budget_sub_category");
    },
    financial_year: function (frm) {
        frm.trigger("set_budget_plan");
    }
});



function load_tranches(frm) {
    if (!frm.doc.grant_agreement) {
        frm.set_value("grant_tranche_name", null);
        frm.tranche_map = {};
        return;
    }

    frappe.call({
        method: "frappe.client.get",
        args: { doctype: "Grant Agreement", name: frm.doc.grant_agreement },
        callback: function (response) {
            if (response.message) {
                let agreement = response.message;
                let tranches = agreement.tranche_table || [];

                frm.tranche_map = {}; // Initialize tranche map
                let options = tranches.map(tr => {
                    frm.tranche_map[tr.tranche_name] = tr.tranche_amount;
                    return tr.tranche_name;
                });

                if (frm.fields_dict.grant_tranche_name) {
                    frm.fields_dict.grant_tranche_name.df.options = options.join("\n");
                    frm.fields_dict.grant_tranche_name.refresh();
                }

                if (tranches.length > 0) {
                    frm.set_value("grant_tranche_name", tranches[0].tranche_name);
                }
            }
        }
    });

}





frappe.ui.form.on('Utilisation Record', {
    set_financial_year: function (frm) {
        frappe.db.get_list("Financial Year", {
            fields: ["financial_year"],
            order_by: "financial_year DESC"
        }).then(response => {
            let financialYears = response.map(doc => doc.financial_year);  // Extract array of years
            // Convert array to a newline-separated string
            let options_string = financialYears.join("\n");

            // Set the select field options correctly
            frm.set_df_property("financial_year", "options", options_string);
        });

    },

    set_budget_plan: function (frm) {
        frappe.db.get_list("Budget Plan", {
            fields: ["name"],
            filters: {
                financial_year: frm.doc.financial_year,
                docstatus: 1
            }
        }).then(response => {
            let budgetPlans = response.map(doc => doc.name);
            frm.set_df_property("budget", "options", budgetPlans.length ? budgetPlans.join("\n") : "");
        });
    },

    set_budget_sub_category: function (frm) {
        frappe.db.get_list("Budget Sub-Category", {
            fields: ["budget_sub_category"],
            filters: {
                budget_category: frm.doc.budget_category

            }
        }).then(response => {
            let budgetSubCategories = response.map(doc => doc.budget_sub_category);
            frm.set_df_property("budget_sub_category", "options", budgetSubCategories.length ? budgetSubCategories.join("\n") : "");
        });
    },

    set_donor_list: function (frm) {
        frappe.db.get_list("Donor", {
            fields: ["donor_name"],
            order_by: "donor_name"
        }).then(response => {
            let donors = response.map(doc => doc.donor_name);
            frm.set_df_property("donor", "options", donors.length ? donors.join("\n") : "");
        })
    },

    budget: function (frm) {
        if (frm.doc.budget) {
            // Fetch selected Budget details
            frappe.db.get_doc("Budget Plan", frm.doc.budget).then(budget => {
                if (budget.financial_year !== frm.doc.financial_year) {
                    frappe.show_alert(__("Selected Budget does not match the selected Financial Year."), 5);
                    frm.set_value("budget", null);
                } else {
                    // Extract unique budget categories from budget breakdown
                    let budget_categories = [...new Set(budget.budget_breakdown.map(item => item.budget_category))];

                    // Update Budget Category dropdown options
                    frm.set_df_property("budget_category", "options", budget_categories.length ? budget_categories.join("\n") : "");
                    frm.dashboard.clear_headline();
                    render_budget_info(frm, budget);
                }
            });
        } else {
            // If budget is removed, reset the filter to maintain strict financial year dependency
            frm.set_query("budget", function () {
                return { filters: { financial_year: frm.doc.financial_year } };
            });

            // Clear dependent fields when budget is removed
            frm.set_value("budget_category", null);
            frm.set_df_property("budget_category", "options", "");
        }
    },
    after_workflow_action: function (frm) {
        frm.reload_doc(); // Reloads the document after reopening
    },
    create_expense_record: function (frm) {
        if (frm.doc.financial_year && frm.doc.budget && frm.doc.donor && frm.doc.grant_agreement && frm.doc.grant_tranche_name && frm.doc.quarters && frm.doc.budget_category && frm.doc.budget_sub_category && frm.doc.expenditure) {


            let data = {
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
            frm.refresh_field('utilisation_child_table');

            // clear the field values
            frm.set_value("grant_tranche_name", null);
            frm.set_value("budget_category", null);
            frm.set_value("budget_sub_category", null);
            frm.set_value("expenditure", null);
        }
        else {
            // set focus on the first empty field
            if (!frm.doc.financial_year) {
                frm.fields_dict.financial_year.set_focus();
            } else if (!frm.doc.budget) {
                frm.fields_dict.budget.set_focus();
            } else if (!frm.doc.budget_category) {
                frm.fields_dict.budget_category.set_focus();
            } else if (!frm.doc.budget_sub_category) {
                frm.fields_dict.budget_sub_category.set_focus();
            } else if (!frm.doc.quarters) {
                frm.fields_dict.quarters.set_focus();
            } else if (!frm.doc.donor) {
                frm.fields_dict.donor.set_focus();
            } else if (!frm.doc.grant_agreement) {
                frm.fields_dict.grant_agreement.set_focus();
            } else if (!frm.doc.grant_tranche_name) {
                frm.fields_dict.grant_tranche_name.set_focus();
            } else if (!frm.doc.expense_title) {
                frm.fields_dict.expense_title.set_focus();
            } else if (!frm.doc.expense_date) {
                frm.fields_dict.expense_date.set_focus();
            } else if (!frm.doc.expenditure) {
                frm.fields_dict.expenditure.set_focus();
            } else {
                frappe.throw("Please fill in all the required fields.");
            }
        }
    },

});


function getCurrencySymbol(callback) {
    frappe.call({
        method: "frappe.client.get_value",
        args: {
            doctype: "Currency",
            fieldname: "symbol",
            filters: { name: frappe.defaults.get_default("currency") }
        },
        callback: function (response) {
            let currency_symbol = response.message ? response.message.symbol : "$";
            callback(currency_symbol);
        }
    });
}

function formatCurrency(amount, currency_symbol) {
    let locale = frappe.defaults.get_default("currency") === "INR" ? "en-IN" : "en-US";
    return currency_symbol + " " + (amount ? amount.toLocaleString(locale, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : "0.00");
}

function render_budget_info(frm, budget) {
    getCurrencySymbol(function (currency_symbol) {
        let budget_html = `
            <div class="frappe-control" style="margin-top: 10px; width: 100%;">
                <label class="control-label" style="font-weight: bold;">Budget Details</label>
                <div class="control-value">
                    <table class="table table-bordered table-hover" style="width: 100%;">
                        <thead class="table-light">
                            <tr>
                                <th style="width: 14%; white-space: nowrap;">Budget</th>
                                <th style="width: 14%; white-space: nowrap;">FY</th>
                                <th style="width: 14%; white-space: nowrap;">1st Quarter</th>
                                <th style="width: 14%; white-space: nowrap;">2nd Quarter</th>
                                <th style="width: 14%; white-space: nowrap;">3rd Quarter</th>
                                <th style="width: 14%; white-space: nowrap;">4th Quarter</th>
                                <th style="width: 16%; white-space: nowrap;">Total Budget</th>
                            </tr>
                        </thead>
                        <tbody>
                                 <tr>
                                    <td style="width: 14%; white-space: nowrap;">${budget.name}</td>
                                    <td style="width: 14%; white-space: nowrap;">${budget.financial_year}</td>
                                    <td style="width: 14%; white-space: nowrap;">${formatCurrency(budget.total_quarter_1_budget, currency_symbol)}</td>
                                    <td style="width: 14%; white-space: nowrap;">${formatCurrency(budget.total_quarter_2_budget, currency_symbol)}</td>
                                    <td style="width: 14%; white-space: nowrap;">${formatCurrency(budget.total_quarter_3_budget, currency_symbol)}</td>
                                    <td style="width: 14%; white-space: nowrap;">${formatCurrency(budget.total_quarter_4_budget, currency_symbol)}</td>
                                    <td style="width: 14%; white-space: nowrap;">${formatCurrency(budget.yearly_budget, currency_symbol)}</td>
                               </tr>
                           </tbody>
                           <tfoot>
                            <tr>
                                <td colspan="7" style="text-align: left; font-style: italic;">
                                    Note: All budget values are displayed in ${currency_symbol}. FY = Financial Year
                                </td>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            </div>
        `;
        if (!frm.fields_dict["budget_table_view_section"]) {
            console.error("donor_table_view_section is not found in form fields.");
            return;
        }

        frm.fields_dict["budget_table_view_section"].$wrapper.html(budget_html);
    });
}


function render_tranche_table(frm, grant) {
    if (!frm.fields_dict["grant_table_view_section"]) {
        console.error("donor_table_view_section is not found in form fields.");
        return;
    }

    let tranche_data = grant.tranche_table;

    if (!tranche_data || tranche_data.length === 0) {
        console.warn("No tranche data available.");
        return;
    }

    // Get currency symbol
    getCurrencySymbol(function (currency_symbol) {
        let table_html = `
        <div class="frappe-control" style="margin-top: 10px; width: 100%;">
            <label class="control-label" style="font-weight: bold;">Tranche Details</label>
            <div class="control-value">
                <table class="table table-bordered table-hover" style="width: 100%; text-align: center;">
                    <thead class="table-light">
                        <tr>
                            <th style="width: 14%; white-space: nowrap;">Tranche Info</th>`;

        // Create column headers dynamically
        tranche_data.forEach(tranche => {
            table_html += `<th style="width: ${80 / tranche_data.length}%; white-space: nowrap;">${tranche.tranche_name}</th>`;
        });

        table_html += `</tr></thead><tbody>`;

        // Row 1: Tranche Amounts
        table_html += `<tr><td><b>Amount</b></td>`;
        tranche_data.forEach(tranche => {
            table_html += `<td>${formatCurrency(tranche.tranche_amount, currency_symbol)}</td>`;
        });
        table_html += `</tr>`;

        //Row 2: Status
        table_html += `<tr><td><b>Status</b></td>`;
        tranche_data.forEach(tranche => {
            table_html += `<td>${tranche.tranche_status}</td>`;
        });
        table_html += `</tr>`;

        // // Row 3: Financial Year
        // table_html += `<tr><td><b>Financial Year</b></td>`;
        // tranche_data.forEach(tranche => {
        //     table_html += `<td>${tranche.tranche_financial_year}</td>`;
        // });
        // table_html += `</tr>`;

        // // Row 4: Received On
        // table_html += `<tr><td><b>Received On</b></td>`;
        // tranche_data.forEach(tranche => {
        //     table_html += `<td>${tranche.received_on || "-"}</td>`;
        // });
        // table_html += `</tr>`;

        // // Row 5: Expenditure
        // table_html += `<tr><td><b>Expenditure</b></td>`;
        // tranche_data.forEach(tranche => {
        //     table_html += `<td>${formatCurrency(tranche.total_tranche_expenditure, currency_symbol)}</td>`;
        // });
        // table_html += `</tr>`;

        table_html += `</tbody></table></div></div>`;
        frm.fields_dict["grant_table_view_section"].$wrapper.html(table_html);
    });
}


function render_expense_button(frm) {
    frappe.call({
        method: 'funder_management_system.utilisation_module.doctype.utilisation_record.utilisation_record.count_expense_items',
        args: {
            urn: frm.doc.name
        },
        callback: function (response) {
            const counts = response.message; // This will be the dictionary returned by the server-side method

            // Define button labels and colors
            const buttonConfigs = [
                { label: 'Submitted Expense Items', status: 1, color: 'btn-primary', count: counts[1] },
                { label: 'Cancelled Expense Items', status: 2, color: 'btn-danger', count: counts[2] }
            ];

            // Add buttons dynamically with updated counts
            buttonConfigs.forEach(config => {
                let button = frm.add_custom_button(`${__(config.label)} (${config.count})`, function () {
                    frappe.set_route('List', 'Expense Item', { urn: frm.doc.name, docstatus: config.status });
                });

                $(button).removeClass('btn-default').addClass(config.color);
            });
        }
    });
}

frappe.realtime.on("reload_utilisation", (data) => {
    if (cur_frm && cur_frm.doc.name === data.utilisation) {
        cur_frm.reload_doc();
    }
});

// Copyright (c) 2025, Tech4Good Community and contributors
// For license information, please see license.txt

frappe.ui.form.on("Grant Disbursement Receipt", {
    refresh: function(frm) {
        frm.set_df_property('select_budget', 'read_only', 1);
        frm.set_df_property("financial_year", "only_select", 1);
        frm.set_df_property("select_budget", "only_select", 1);
        if (!frm.doc.financial_year) {
            frm.set_df_property("select_budget", "hidden", 1);
        }
    },
    donor: function(frm) {
        frm.set_query('grant_agreement', () => {
            return frm.doc.donor ? { filters: { donor: frm.doc.donor } } : {};
        });
        frm.set_value('grant_agreement', null);
        frm.set_value('tranche_name', null);
    },

    grant_agreement: function(frm) {
        frm.set_query('tranche_name', () => {
            return frm.doc.grant_agreement ? { filters: { parent: frm.doc.grant_agreement } } : {};
        });
        frm.set_value('tranche_name', null);
        load_tranches(frm);
    },

    // tranche_name: function(frm) {
    //     if (frm.doc.tranche_name && frm.tranche_map) {
    //         frm.set_value("tranche_amount", frm.tranche_map[frm.doc.tranche_name] || null);
    //         // render the grant details
    //         frappe.db.get_doc("Budget Plan", frm.doc.select_budget).then(budget => {
    //             if (budget) {
    //                 frm.dashboard.clear_headline();
    //                 render_grant_info(frm, budget);
    //             }
    //         });



    //     } else {
    //         frm.set_value("tranche_amount", null);
    //     }
    // },

    budget_category: function(frm) {
        frm.set_query('budget_sub_category', () => {
            return frm.doc.budget_category ? { filters: { budget_category: frm.doc.budget_category } } : {};
        });
        frm.set_value('budget_sub_category', null);
    },
    financial_year: function(frm) {
        
            frm.set_df_property("select_budget", "hidden", 0);
        
        if (frm.doc.financial_year) {
            frm.set_query("select_budget", function() {
                return {
                    filters: {
                        financial_year: frm.doc.financial_year,
                        docstatus: 1
                    }
                };
            });
        }
    },
});



function load_tranches(frm) {
    if (!frm.doc.grant_agreement) {
        frm.set_value("tranche_name", null);
        frm.set_value("tranche_amount", null);
        frm.tranche_map = {};
        return;
    }

    frappe.call({
        method: "frappe.client.get",
        args: { doctype: "Grant Agreement", name: frm.doc.grant_agreement },
        callback: function(response) {
            if (response.message) {
                let agreement = response.message;
                let tranches = agreement.tranche_table || [];

                frm.tranche_map = {}; // Initialize tranche map
                let options = tranches.map(tr => {
                    frm.tranche_map[tr.tranche_name] = tr.tranche_amount;
                    return tr.tranche_name;
                });

                if (frm.fields_dict.tranche_name) {
                    frm.fields_dict.tranche_name.df.options = options.join("\n");
                    frm.fields_dict.tranche_name.refresh();
                }

                if (tranches.length > 0) {
                    frm.set_value("tranche_name", tranches[0].tranche_name);
                    frm.set_value("tranche_amount", tranches[0].tranche_amount);
                }
            }
        }
    });

}





frappe.ui.form.on('Grant Disbursement Receipt', {
    select_budget: function (frm) {
        if (frm.doc.select_budget) {
            frappe.db.get_doc("Budget Plan", frm.doc.select_budget).then(budget => {
                if (budget) {
                    frm.dashboard.clear_headline();
                    render_budget_info(frm, budget);
                }
            });
        }
    },
    grant_agreement: function (frm) {
        if (frm.doc.select_budget) {
            frappe.db.get_doc("Budget Plan", frm.doc.select_budget).then(budget => {
                if (budget) {
                    console.log("grant_agreement");
                    console.log(budget);
                    frm.dashboard.clear_headline();
                    render_grant_info(frm, budget);
                }
            });
        }
    }
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
                                <th style="width: 14%;">Budget</th>
                                <th style="width: 14%;">FY</th>
                                <th style="width: 14%;">1st Quarter</th>
                                <th style="width: 14%;">2nd Quarter</th>
                                <th style="width: 14%;">3rd Quarter</th>
                                <th style="width: 14%;">4th Quarter</th>
                                <th style="width: 16%;">Total Budget</th>
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
        frm.fields_dict["budget_table_view_section"].$wrapper.html(budget_html);
    });
}

function render_grant_info(frm, grant) {
    getCurrencySymbol(function (currency_symbol) {
        let grant_html = `<div>Hello</div>`;  // Add grant-related HTML here
        frm.fields_dict["donor_table_view_section"].$wrapper.html(grant_html);
    });
}






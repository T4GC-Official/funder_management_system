// Copyright (c) 2025, Tech4Good Community and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Grant Disbursement Receipt - New", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Grant Disbursement Receipt - New', {
    donor: function(frm) {
        // Filter Grant Agreement based on Donor selection
        if (frm.doc.donor) {
            frm.set_query('grant_agreement', function() {
                return {
                    filters: {
                        donor: frm.doc.donor
                    }
                };
            });
        } else {
            frm.set_query('grant_agreement', function() {
                return {};
            });
        }
        frm.set_value('grant_agreement', null);
        frm.set_value('tranche_name', null);
    },

    grant_agreement: function(frm) {
        // Filter Tranche Name based on selected Grant Agreement
        if (frm.doc.grant_agreement) {
            frm.set_query('tranche_name', function() {
                return {
                    filters: {
                        parent: frm.doc.grant_agreement  // Filters from child table
                    }
                };
            });
        } else {
            frm.set_query('tranche_name', function() {
                return {};
            });
        }
        frm.set_value('tranche_name', null);
    },
    
    budget_category: function(frm) {
        if (frm.doc.budget_category) {
            frm.set_query('budget_sub_category', function() {
                return {
                    filters: {
                        budget_category: frm.doc.budget_category
                    }
                };
            });
        } else {
            frm.set_query('budget_sub_category', function() {
                return {};
            });
        }
        frm.set_value('budget_sub_category', null); // Reset sub category on category change
    }

});




function load_tranches(grant_agreement, tranche_control, available_amount_control, frm) {
    frappe.call({
        method: "frappe.client.get",
        args: { doctype: "Grant Agreement", name: grant_agreement },
        callback: function (response) {
            if (response.message) {
                console.log("Inside GA Tranche ", response);
                let agreement = response.message;
                let tranches = agreement.tranche_table || []; // Ensure correct child table fieldname

                // Store tranche data for reference
                frm.tranche_map = {};  // Store in form instance
                let options = tranches.map(tr => {
                    frm.tranche_map[tr.tranche_name] = tr.tranche_amount;
                    return tr.tranche_name;
                });

                // Set tranche dropdown options dynamically (newline-separated list)
                tranche_control.df.options = options.join("\n");
                tranche_control.refresh();

                // Set first tranche as default (if available)
                if (tranches.length > 0) {
                    tranche_control.set_value(tranches[0].tranche_name);
                    available_amount_control.set_value(tranches[0].tranche_amount);
                }
            }
        }
    });
}

// Trigger function when grant agreement changes
frappe.ui.form.on("Grant Disbursement Receipt - New", {
    grant_agreement: function (frm) {
        if (frm.doc.grant_agreement) {
            load_tranches(frm.doc.grant_agreement, frm.fields_dict.tranche_name, frm.fields_dict.tranche_amount, frm);
        } else {
            frm.set_value("tranche_name", null);
            frm.set_value("tranche_amount", null);
            frm.tranche_map = {}; // Clear stored tranche data
        }
    },

    tranche_name: function (frm) {
        if (frm.doc.tranche_name && frm.tranche_map) {
            // Retrieve tranche amount from stored map
            let tranche_amount = frm.tranche_map[frm.doc.tranche_name] || null;
            frm.set_value("tranche_amount", tranche_amount);
        } else {
            frm.set_value("tranche_amount", null);
        }
    },
    
});








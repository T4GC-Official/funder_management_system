// Copyright (c) 2025, Tech4Good Community and contributors
// For license information, please see license.txt

frappe.ui.form.on("Grant Disbursement Receipt - New", {
    onload: function(frm) {
        frm.trancheData = {};
        frm.categoryData = {};
    },

    donor: function(frm) {
        frm.set_query("grant_agreement", () => ({
            filters: { donor: frm.doc.donor || undefined }
        }));
        frm.set_value("grant_agreement", null);
        frm.set_value("tranche_name", null);
    },

    grant_agreement: function(frm) {
        frm.set_query("tranche_name", () => ({
            filters: { parent: frm.doc.grant_agreement || undefined }
        }));
        frm.set_value("tranche_name", null);
        frm.set_value("tranche_amount", null);
        frm.trigger("load_tranches");
    },

    tranche_name: function(frm) {
        if (frm.doc.tranche_name && frm.tranche_map) {
            frm.set_value("tranche_amount", frm.tranche_map[frm.doc.tranche_name] || null);
        } else {
            frm.set_value("tranche_amount", null);
        }
    },

    budget_category: function(frm) {
        frm.set_query("budget_sub_category", () => ({
            filters: { budget_category: frm.doc.budget_category || undefined }
        }));
        frm.set_value("budget_sub_category", null);
    },

    budget_plan: function(frm) {
        frm.trigger("fetch_budget_and_tranche_details");
    },

    fetch_budget_and_tranche_details: function (frm) {
    if (!frm.doc.budget_plan || !frm.doc.grant_agreement) {
        frm.set_df_property("budget_and_tranche_summary", "options", 
            "<p style='color: red;'>Please select Budget Plan and Grant Agreement.</p>");
        return;
    }

    frappe.call({
        method: "funder_management_system.utilisation_module.doctype.grant_disbursement_receipt.grant_disbursement_receipt.get_budget_and_tranche_details",
        args: {
            grant: frm.doc.grant_agreement,
            budget_plan: frm.doc.budget_plan
        },
        callback: function (r) {
            if (!r.message) {
                frm.set_df_property("budget_and_tranche_summary", "options", 
                    "<p style='color: red;'>No data available.</p>");
                return;
            }

            console.log("Received data:", r.message);

            // Store data in global variables instead of frm
            trancheData = r.message.tranche_data || {};
            categoryData = r.message.category_data || {};

            // Trigger UI update based on the first available tranche
            frm.trigger("update_budget_summary");
        }
    });
},

    update_budget_summary: function(frm) {
    if (Object.keys(trancheData).length === 0 || Object.keys(categoryData).length === 0) return;

    let selected_tranche = frm.doc.tranche_name;
    let selected_category = frm.doc.budget_category;
    let selected_sub_category = frm.doc.budget_sub_category;

    // Filter tranche data based on selection
    let filteredTrancheData = selected_tranche ? { [selected_tranche]: trancheData[selected_tranche] } : trancheData;

    // Build Tranche Utilisation Table
    let tranche_html = `<h4>Tranche-Wise Utilisation</h4>
        <table class='table table-bordered'>
        <tr><th>Tranche</th><th>Allocated</th><th>Utilised</th><th>Remaining</th></tr>`;

    for (let tranche in filteredTrancheData) {
        let t = filteredTrancheData[tranche];
        tranche_html += `<tr>
            <td>${tranche}</td>
            <td>${t.allocated}</td>
            <td>${t.utilised}</td>
            <td style="color:${t.remaining < 0 ? 'red' : 'green'}">${t.remaining}</td>
        </tr>`;
    }

    tranche_html += `</table>`;

    // Convert categoryData object into an array for filtering
    let category_list = Object.values(categoryData);

    // Filter category data based on selection
    if (selected_category || selected_sub_category) {
        category_list = category_list.filter(c => 
            (!selected_category || c.category === selected_category) &&
            (!selected_sub_category || c.sub_category === selected_sub_category)
        );
    }

    // Build Budget Category Utilisation Table
    let category_html = `<h4>Budget Category Utilisation</h4>
        <table class='table table-bordered'>
        <tr><th>Category</th><th>Sub-Category</th><th>Allocated</th><th>Utilised</th><th>Remaining</th><th>Status</th></tr>`;

    for (let c of category_list) {
        category_html += `<tr>
            <td>${c.category}</td>
            <td>${c.sub_category || '-'}</td>
            <td>${c.allocated}</td>
            <td>${c.utilised}</td>
            <td style="color:${c.remaining < 0 ? 'red' : 'green'}">${c.remaining}</td>
            <td><b style="color:${c.status === 'Overspent' ? 'red' : 'green'}">${c.status}</b></td>
        </tr>`;
    }

    category_html += `</table>`;

    // Update the UI
    frm.set_df_property("budget_and_tranche_summary", "options", tranche_html + category_html);
    frm.refresh_field("budget_and_tranche_summary");
    },

// Triggers for dynamic filtering
    tranche_name: function(frm) { frm.trigger("update_budget_summary"); },
    budget_category: function(frm) { frm.trigger("update_budget_summary"); },
    budget_sub_category: function(frm) { frm.trigger("update_budget_summary"); },

    
    load_tranches: function(frm) {
        if (!frm.doc.grant_agreement) return;

        frappe.call({
            method: "frappe.client.get",
            args: { doctype: "Grant Agreement", name: frm.doc.grant_agreement },
            callback: function(response) {
                if (response.message) {
                    let tranches = response.message.tranche_table || [];
                    frm.tranche_map = Object.fromEntries(tranches.map(tr => [tr.tranche_name, tr.tranche_amount]));

                    let options = tranches.map(tr => tr.tranche_name).join("\n");
                    frm.fields_dict.tranche_name.df.options = options;
                    frm.fields_dict.tranche_name.refresh();

                    if (tranches.length > 0) {
                        frm.set_value("tranche_name", tranches[0].tranche_name);
                        frm.set_value("tranche_amount", tranches[0].tranche_amount);
                    }
                }
            }
        });
    }
});

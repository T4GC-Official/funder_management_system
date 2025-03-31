// Copyright (c) 2025, Tech4Good Community and contributors
// For license information, please see license.txt

frappe.ui.form.on("Donor", {
    refresh: function(frm) {
        frm.get_field("table_donor_history").grid.cannot_add_rows = true;
        frm.trigger("item_frequency");
        frm.trigger("load_engagement_checklist");
        frm.trigger("save_donor_history");
    },
    before_save: function (frm) {
        frm.trigger("save_donor_history");
    },
	pan_card: function(frm) {
        let pan = frm.doc.pan_card;

        if (pan) {
            let pan_regex = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/;

            if (!pan_regex.test(pan)) {
                frappe.msgprint({
                    title: __("Invalid PAN Number"),
                    message: __("PAN Number must follow the format: ABCDE1234F"),
                    indicator: "red"
                });

                frm.set_value("pan_card", "");  // Reset invalid PAN
            }
        }
    },
    setup: function(frm) {
        frm.set_query("lead_name", function() {
            return {
                filters: {
                    lead_stage: "Confirmed Lead"
                }
            };
        });
    },
    save_donor_history: function (frm) {
        let { donor_status } = frm.doc;
        if (frm.doc.table_donor_history.length === 0) {
            let donor_history = frm.add_child("table_donor_history");
            donor_history.donor_status = donor_status;
            frappe.refresh_field("table_donor_history");
        }
        // if child table is not empty then check the lead stage and financial year and lead category if there is any change then add a new row with data
        else {
            let last_donor_history = frm.doc.table_donor_history[frm.doc.table_donor_history.length - 1];
            if (donor_status !== last_donor_history.donor_status)
                {
                    let donor_history = frm.add_child("table_donor_history");
                    donor_history.donor_status = donor_status;
            }
        }


    },
    load_engagement_checklist: function(frm) {
        if (!frm.is_new() && frm.doc.engagement_checklist_table.length === 0){
            frappe.call({
                method: "frappe.client.get_list",
                args:{
                    doctype: "Engagement Checklist Master",
                    fields: ["checklist_item"],
                },
                callback: function(r){
                    if(r.message){
                        frm.clear_table("engagement_checklist_table");
                        r.message.forEach((item) => {
                            let row = frm.add_child("engagement_checklist_table");
                            row.item = item.checklist_item;
                        });
                        frm.refresh_field("engagement_checklist_table");
                    }
                }
            })
        }
}});

frappe.ui.form.on("Engagement Checklist", {
    item_frequency: function(frm, cdt, cdn) {

        let row = locals[cdt][cdn];  // Get the specific child table row
        let days_to_add = get_days_to_add(row.item_frequency);
        let next_reminder_date = frappe.datetime.add_days(frappe.datetime.get_today(), days_to_add);
        frappe.model.set_value(cdt, cdn, "next_reminder_date", next_reminder_date);
        frm.refresh_field("engagement_checklist_table");  // Replace with your actual child table fieldname
    }
});


/**
 * Returns the number of days to add based on the item frequency.
 */
function get_days_to_add(frequency) {
    const frequency_mapping = {
        "Monthly": 30,
        "Quarterly": 90,
        "Half Yearly": 180,
        "Yearly": 365
    };

    return frequency_mapping[frequency] || 0;  // Default to 0 if frequency is not found
}

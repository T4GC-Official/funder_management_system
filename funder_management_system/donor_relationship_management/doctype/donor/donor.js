// Copyright (c) 2025, Tech4Good Community and contributors
// For license information, please see license.txt

frappe.ui.form.on("Donor", {
    refresh: function(frm) {
        frm.trigger("item_frequency");
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
    }
});

frappe.ui.form.on("Engagement Checklist", {
    item_frequency: function(frm, cdt, cdn) {
        console.log("Item Frequency changed!");

        let row = locals[cdt][cdn];  // Get the specific child table row
        let days_to_add = get_days_to_add(row.item_frequency);
        let next_reminder_date = frappe.datetime.add_days(frappe.datetime.get_today(), days_to_add);

        console.log(`Selected Frequency: ${row.item_frequency}, Days to Add: ${days_to_add}, Next Reminder Date: ${next_reminder_date}`);

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

// Copyright (c) 2025, Tech4Good Community and contributors
// For license information, please see license.txt


frappe.ui.form.on("Organisation Details", {
    before_save: function(frm) {
        let pan = frm.doc.pan_card;

        if (pan) {
            let pan_regex = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/;

            if (!pan_regex.test(pan)) {
                frappe.show_alert({
                    message: __("Invalid PAN Number. Please enter a valid PAN Number in format: ABCDE1234F"),
                    indicator: 'red'
                });

                frm.set_value("pan_card", "");  // Reset invalid PAN
                // prevent from from saving
                frappe.validated = false
                // focus on pan card field
                frm.fields_dict["pan_card"].set_focus();
            }
        }
    }
});

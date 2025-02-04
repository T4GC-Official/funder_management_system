// Copyright (c) 2025, Tech4Good Community and contributors
// For license information, please see license.txt


frappe.ui.form.on("Organisation Details", {
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
    }
});

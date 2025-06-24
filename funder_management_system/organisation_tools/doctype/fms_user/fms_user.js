// Copyright (c) 2025, Tech4Good Community and contributors
// For license information, please see license.txt

frappe.ui.form.on("FMS User", {
	after_save: function(frm) {
        console.log("FMS User form saved successfully.");
		frappe.call({
			method: "funder_management_system.organisation_tools.doctype.user_creation.user_creation.create_fms_user",
			args: {
				doc_name: frm.doc.name
			},
			callback: function(response) {
				if (response.message && response.message.includes("created")) {
					frappe.show_alert({
						message: __("User created successfully!"),
						indicator: "green"
					});
				} else {
					frappe.show_alert({
						message: __("User creation failed or already exists."),
						indicator: "red"
					});
				}
			}
		});
	}
});


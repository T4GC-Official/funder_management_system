// Copyright (c) 2025, Tech4Good Community and contributors
// For license information, please see license.txt

frappe.ui.form.on("Organisation Lead", {
    organisation_name: function (frm) {
        if(!frm.doc.organisation_name){
            frm.refresh_field("website_url");
        }
    }
});
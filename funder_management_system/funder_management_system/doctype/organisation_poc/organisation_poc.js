// Copyright (c) 2025, Tech4Good Community and contributors
// For license information, please see license.txt

frappe.ui.form.on("Organisation POC", {
	validate: function (frm) {
        if(frm.doc.phone){
            phone = frm.doc.phone.slice(-10);
            if(phone.length < 10){
                frappe.msgprint("Phone number is invalid");
                frappe.validated = false;
            }
        }  
    },
});

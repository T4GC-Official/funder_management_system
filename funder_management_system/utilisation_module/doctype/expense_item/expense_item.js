// Copyright (c) 2025, Tech4Good Community and contributors
// For license information, please see license.txt

frappe.ui.form.on("Expense Item", {
    on_submit: function(frm) {
        frappe.call({
            method: "funder_management_system.utilisation_module.doctype.expense_item.expense_item.submit_record",
            args: { 
                "document_name": frm.doc.name
            },
            freeze: true,
            async: true,
            callback: function(r) {
                if(r.message) {
                    frappe.msgprint(__('Expense Item submitted successfully.'));
                }
            }
        });
    }
 });

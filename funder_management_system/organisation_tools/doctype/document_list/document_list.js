// frappe.ui.form.on("Document List", {
//     refresh: function (frm) {
//         frm.trigger("calculate_notification_dates");
//     },
//     before_save: function (frm) {
//         console.log("before_save");
//         frm.trigger("calculate_notification_dates"); // Ensure it's calculated before saving
//     },
//     calculate_notification_dates: function (frm) {
//         console.log("calculate_notification_dates");
//         if (frm.doc.organisation_docs && frm.doc.organisation_docs.length > 0) {
//             frm.doc.organisation_docs.forEach(row => {
//                 console.log(row.renewal_date, row.notify_me_before);
//                 if (row.renewal_date && row.notify_me_before) {
//                     let renewal_date = frappe.datetime.str_to_obj(row.renewal_date);
//                     let notification_date = frappe.datetime.add_days(renewal_date, -row.notify_me_before);

//                     frappe.model.set_value(row.doctype, row.name, "notification_trigger_date", frappe.datetime.obj_to_str(notification_date));
//                 }
//             });
//             frm.refresh_field("organisation_toolkit");
//         }
//     }
// });

frappe.ui.form.on("Organisation Toolkit", {
    renewal_date: function (frm, cdt, cdn) {
        //console.log("renewal_date triggered");
        calculate_notification_dates(frm);
    },
    notify_me_before: function (frm, cdt, cdn) {
        calculate_notification_dates(frm);
    }
});

function calculate_notification_dates(frm) {
    console.log("calculate_notification_dates triggered");
    if (frm.doc.organisation_docs && frm.doc.organisation_docs.length > 0) {
        frm.doc.organisation_docs.forEach(row => {
            if (row.renewal_date && row.notify_me_before) {
                let renewal_date = frappe.datetime.str_to_obj(row.renewal_date);
                let notification_date = frappe.datetime.add_days(renewal_date, -row.notify_me_before);

                frappe.model.set_value(row.doctype, row.name, "notification_trigger_date", frappe.datetime.obj_to_str(notification_date));
            }
        });
        frm.refresh_field("organisation_docs");
    }
}


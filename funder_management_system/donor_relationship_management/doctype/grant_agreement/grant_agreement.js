// Copyright (c) 2025, Tech4Good Community and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Grant Agreement", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Grant Agreement', {
    refresh: function(frm) {
        frm.trigger("number_of_tranch");  // Ensures the child table is updated on form load
    },
    number_of_tranche: function(frm) {
        let count = frm.doc.total_number_of_tranches || 0;  // Get the number of tranches
        let child_table = frm.doc.tranche_table || [];  // Get existing child table data

        if (child_table.length < count) {
            for (let i = child_table.length; i < count; i++) {
                let new_row = frm.add_child("tranche_table");
                new_row.tranche_amount = 0;  // Default amount
                new_row.tranche_status = "Pending";  // Default status
             //@To Do - Add more default values here and if there is data in this child table then copy these data to the child table
             // In case the Ax ask to keep the previous record then only we will implement it.
            }
        } 
        // Remove extra rows if needed
        else if (child_table.length > count) {
            frm.doc.tranche_table = frm.doc.tranche_table.slice(0, count);
        }
        frm.fields_dict["tranche_table"].grid.cannot_add_rows = true;  // disable the add row button
        frm.refresh_field("tranche_table");  // Refresh the child table
    },
    
    total_number_of_tranches: function(frm) {
        frappe.msgprint("Field value of 'Total Number of Tranches' has been changed!");
        frm.trigger("number_of_tranche");
    },
    grant_agreement_end_date: function(frm) {
        if (frm.doc.grant_agreement_start_date && frm.doc.grant_agreement_end_date < frm.doc.grant_agreement_start_date) {
            frappe.msgprint(__('Grant Agreement End Date cannot be before Start Date'));
            frm.set_value('grant_agreement_end_date', null);
        }
    },
    grant_agreement_start_date: function(frm) {
        const financial_year_of_grant_agreement = getFinancialYear(frm.doc.grant_agreement_start_date);
        if (frm.doc.grant_agreement_end_date && frm.doc.grant_agreement_end_date < frm.doc.grant_agreement_start_date) {
            frappe.msgprint(__('Grant Agreement Start Date cannot be after end Date'));
            frm.set_value('grant_agreement_end_date', null);
            frm.set_value('grant_agreement_start_date', null);
        }
        frm.set_value('financial_year_of_grant_agreement', financial_year_of_grant_agreement);
    },

});
function getFinancialYear(dateString) {
    if(!dateString) {
    return null;
    }
    // Parse the date string into a Date object
    const date = new Date(dateString);
    // Get the year and month from the parsed date
    let year = date.getFullYear();
    let month = date.getMonth() + 1; // getMonth() is 0-based, so we add 1
    // Check if we are before April (i.e., in the previous financial year)
    if (month < 4) {
      year -= 1; // The financial year started in the previous year
    }
    // Format the financial year as 'YYYY-YY'
    const startYear = year;
    const endYear = year + 1;
    return `${startYear}-${String(endYear).slice(2, 4)}`;
  }






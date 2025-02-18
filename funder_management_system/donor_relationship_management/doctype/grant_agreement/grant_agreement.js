frappe.ui.form.on('Grant Agreement', {
    onload: function(frm) {
        frm.fields_dict["tranche_table"].grid.get_field("tranche_financial_year").get_query = function(doc) {
            return {
                filters: [
                    ["Financial Year", "year_start_date", ">=", frm.doc.grant_agreement_start_date],
                    ["Financial Year", "year_end_date", "<=", frm.doc.grant_agreement_end_date]
                ]
            };
        };
    },
    refresh: function(frm) {
        frm.trigger("number_of_tranche");
        frm.get_field("tranche_table").grid.cannot_add_rows = true;  // Disable add row button
        frm.refresh_field("tranche_table");  // Refresh the child table
    },
    number_of_tranche: function(frm) {
        let count = frm.doc.total_number_of_tranches || 0;  // Get the number of tranches
        let child_table = frm.doc.tranche_table || [];  // Get existing child table data

        if (child_table.length < count) {
            for (let i = child_table.length; i < count; i++) {
                let new_row = frm.add_child("tranche_table");
                new_row.tranche_amount = 0;  // Default amount
                new_row.tranche_status = "Pending";  // Default status
            }
        } 
        // Remove extra rows if needed
        else if (child_table.length > count) {
            frm.doc.tranche_table = frm.doc.tranche_table.slice(0, count);
        }

        frm.get_field("tranche_table").grid.cannot_add_rows = true;  // Ensure the button is disabled
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
            frappe.msgprint(__('Grant Agreement Start Date cannot be after End Date'));
            frm.set_value('grant_agreement_end_date', null);
            frm.set_value('grant_agreement_start_date', null);
        }
        frm.set_value('financial_year_of_grant_agreement', financial_year_of_grant_agreement);
    },
});

function getFinancialYear(dateString) {
    if (!dateString) {
        return null;
    }
    const date = new Date(dateString);
    let year = date.getFullYear();
    let month = date.getMonth() + 1;
    if (month < 4) {
        year -= 1;
    }
    return `${year}-${String(year + 1).slice(2, 4)}`;
}


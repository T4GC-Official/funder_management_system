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
        frm.get_field("tranche_table").grid.cannot_add_rows = true;  // Disable add row button
        // disable delete row button
        frm.get_field("tranche_table").grid.wrapper.find('.grid-remove-rows').hide();
        // remove check box column from child table
        frm.get_field("tranche_table").grid.wrapper.find('.grid-select-row').hide();
        frm.refresh_field("tranche_table");  // Refresh the child table
        frm.events.progress_bar(frm);// Show progress bar
    },
    before_save: function(frm) {
        frm.trigger("calculate_tranche_progress");
        frm.trigger("check_total_tranche_amount");
        frm.trigger("check_tranche_amount_type");
        
    },

    number_of_tranche: function(frm) {
        let count = frm.doc.total_number_of_tranches || 0;  // Get the number of tranches
        let child_table = frm.doc.tranche_table || [];  // Get existing child table data

        if (child_table.length < count) {
            for (let i = child_table.length; i < count; i++) {
                let new_row = frm.add_child("tranche_table");
                if (child_table.length > 0) {
                    new_row.tranche_name = `Tranche-${i + 1}`;  // Copy tranche name from first row
                    new_row.tranche_amount = child_table[0].tranche_amount;  // Copy amount from first row
                    new_row.tranche_status = child_table[0].tranche_status;  // Copy status from first row
                    new_row.tranche_financial_year = child_table[0].tranche_financial_year;  // Copy status from first row
                } else {
                    new_row.tranche_name = `Tranche ${i + 1}`;  // Default name
                    new_row.tranche_amount = 0;  // Default amount
                    new_row.tranche_status = "Pending";  // Default status
                }
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
        frappe.msgprint("You are changing the 'Total Number of Tranches' this will regenerate the Tranche Table rows. Please review the Tranche Table after saving the document.");
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
    calculate_tranche_progress:function(frm){
        console.log("calculate_tranche_progress");
        let total_tranches = frm.doc.tranche_table ? frm.doc.tranche_table.length : 0;
        let completed_tranches = 0;
        if (total_tranches > 0) {
            completed_tranches = frm.doc.tranche_table.filter(row => row.tranche_status === "Received - On Time").length + frm.doc.tranche_table.filter(row => row.tranche_status === "Received - Delayed").length;
        }
        let progress = total_tranches > 0 ? (completed_tranches / total_tranches) * 100 : 0;
        frm.set_value("tranche_progress", progress);
    },
    progress_bar: function(frm) {
        let progress = frm.doc.tranche_progress || 0;
        frm.dashboard.clear_headline();
        let html = `
            <div class="progress" style="height: 10px;">
                <div class="progress-bar bg-success" role="progressbar" style="width: ${progress}%;" aria-valuenow="${progress}" aria-valuemin="0" aria-valuemax="100">
                </div>
            </div>
            <p style="margin-top:5px;">Total Tranche Money Received: ${progress}%</p>
            <div class="progress" style="height: 10px;">
                <div class="progress-bar bg-warning" role="progressbar" style="width: ${0}%;" aria-valuenow="${100}" aria-valuemin="0" aria-valuemax="100">
                </div>
            </div>
            <p style="margin-top:5px;">Total Tranche Money Utilized: ${0}%</p>
        `;
        frm.fields_dict["tranche_progress_bar"].$wrapper.html(html);
    },

      check_total_tranche_amount: function(frm) {
        let total_tranche_amount = 0;
        frm.doc.tranche_table.forEach(row => {
            total_tranche_amount += row.tranche_amount;
        });
        if (total_tranche_amount > frm.doc.total_grant_amount) {
            // prevent saving the from
            frappe.validated = false;
            frappe.msgprint("Total Tranche Amount cannot be greater than Total Grant Amount");
        }
        //focus the cursor on the total grant amount field
        frm.fields_dict["total_grant_amount"].set_focus();
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


frappe.ui.form.on('Tranche Details', {
    tranche_status: function(frm, cdt, cdn) {
       // if tranche_status is Received - On Time or Received - Delayed,  the Tranche_amount for that row should not be zero
         // and show a message if the amount is zero
        let row = locals[cdt][cdn];
        const allowedStatuses = ["Received - On Time", "Received - Delayed"];
        if (allowedStatuses.includes(row.tranche_status) && row.tranche_amount === 0) {
            frappe.validated = false;
            frappe.msgprint("Tranche Amount cannot be zero for Received - On Time or Received - Delayed status");
        }
          
    }

});








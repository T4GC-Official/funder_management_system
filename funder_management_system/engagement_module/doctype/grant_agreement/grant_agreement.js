frappe.ui.form.on('Grant Agreement', {
    onload: function (frm) {

    },
    refresh: function (frm) {

        frm.get_field("tranche_table").grid.cannot_add_rows = true;  // Disable add row button
        // disable delete row button
        frm.get_field("tranche_table").grid.wrapper.find('.grid-remove-rows').hide();
        // remove check box column from child table
        frm.get_field("tranche_table").grid.wrapper.find('.grid-select-row').hide();
        frm.refresh_field("tranche_table");  // Refresh the child table
        frm.events.progress_bar(frm);
        frm.set_df_property("donor", "only_select", 1);
    },
    before_save: function (frm) {

        if (frm.doc.tranche_table) {
            const today = frappe.datetime.get_today();

            for (let i = 0; i < frm.doc.tranche_table.length; i++) {
                let row = frm.doc.tranche_table[i];

                if (row.due_date && row.received_on) {
                    if (row.received_on <= row.due_date) {
                        row.tranche_status = "Received - On Time";
                    } else {
                        row.tranche_status = "Received - Delayed";
                    }
                } else if (row.due_date && !row.received_on) {
                    if (row.due_date < today) {
                        row.tranche_status = "Pending - Delayed";
                    } else {
                        row.tranche_status = "Pending - On Time";
                    }
                } else {
                    row.tranche_status = "Pending - On Time"; // Default fallback
                }
            }

            frm.refresh_field("tranche_table");
        }





        if (frm.doc.total_number_of_tranches <= 0) {
            frappe.show_alert({
                message: "Total Number of Tranches should be greater than 0",
                indicator: 'yellow',
                delay: 3000
            });
            frappe.validated = false;
            frm.fields_dict["total_number_of_tranches"].set_focus();
            return;
        }

        if (frm.doc.total_grant_amount <= 0) {
            frappe.msgprint({
                message: "Total Grant Amount should be greater than 0",
                title: __('Alert'),
                indicator: 'yellow',
                alert: true,
                position: 'top-center'
            });
            frappe.validated = false;
            frm.fields_dict["total_grant_amount"].set_focus();
            return;
        }

        // write a logic to change the Grant Agreement Type to multi year if start date and end date difference is greater than 1 year
        if (frm.doc.grant_agreement_start_date && frm.doc.grant_agreement_end_date) {
            let start_date = new Date(frm.doc.grant_agreement_start_date);
            let end_date = new Date(frm.doc.grant_agreement_end_date);

            // Calculate the difference in months
            let months_diff = (end_date.getFullYear() - start_date.getFullYear()) * 12 + (end_date.getMonth() - start_date.getMonth());

            // Check if the difference is more than 12 months
            if (months_diff > 12) {
                frm.set_value("grant_agreement_type", "Multi Year");
            } else {
                frm.set_value("grant_agreement_type", "Single Year");
            }
        }



        frm.trigger("calculate_utilisation_of_tranche");
        frm.trigger("calculate_total_tranche_amount");
        frm.trigger("calculate_tranche_progress");
        frm.trigger("check_total_tranche_amount");
        frm.trigger("check_tranche_amount_type");

    },

    number_of_tranche: function (frm) {
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
                    new_row.tranche_name = `Tranche-${i + 1}`;  // Default name
                    new_row.tranche_amount = 0;  // Default amount
                    new_row.tranche_status = "Pending - On Time";  // Default status
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

    total_number_of_tranches: function (frm) {
        frappe.show_alert({
            message: "You are changing the 'Total Number of Tranches' this will regenerate the Tranche Table rows. Please review the Tranche Table after saving the document.",
            indicator: 'yellow',
            delay: 3000
        });
        frm.trigger("number_of_tranche");
    },
    grant_agreement_end_date: function (frm) {
        if (frm.doc.grant_agreement_start_date && frm.doc.grant_agreement_end_date < frm.doc.grant_agreement_start_date || frm.doc.grant_agreement_start_date == frm.doc.grant_agreement_end_date) {
            frappe.msgprint(__('Grant Agreement End Date cannot be before Start Date'));
            frm.set_value('grant_agreement_end_date', null);
            frm.fields_dict["grant_agreement_end_date"].set_focus();
            return;
        }

        if (frm.doc.grant_agreement_start_date && frm.doc.grant_agreement_start_date == frm.doc.grant_agreement_end_date) {
            frappe.msgprint(__('Grant Agreement Start Date & End Date cannot be same'));
            frm.fields_dict["grant_agreement_end_date"].set_focus();
            return;
        }
    },
    grant_agreement_start_date: function (frm) {
        if (frm.doc.grant_agreement_end_date && frm.doc.grant_agreement_end_date < frm.doc.grant_agreement_start_date) {
            frappe.msgprint(__('Grant Agreement Start Date cannot be after End Date'));
            frm.set_value('grant_agreement_end_date', null);
            frm.set_value('grant_agreement_start_date', null);
            frm.fields_dict["grant_agreement_end_date"].set_focus();
            return;
        }
    },
    calculate_tranche_progress: function (frm) {
        let total_tranches = frm.doc.tranche_table ? frm.doc.tranche_table.length : 0;
        let completed_tranches = 0;
        if (total_tranches > 0) {
            completed_tranches = frm.doc.tranche_table.filter(row => row.tranche_status === "Received - On Time").length + frm.doc.tranche_table.filter(row => row.tranche_status === "Received - Delayed").length;
        }
        let tranche_progress_percentage = total_tranches > 0 ? (completed_tranches / total_tranches) * 100 : 0;
        let progress_p_q_format = total_tranches > 0 ? `${completed_tranches}/${total_tranches}` : 0;
        frm.set_value("total_tranche_progress", progress_p_q_format);
        frm.set_value("total_tranche_progress_percentage", tranche_progress_percentage);
    },
    calculate_utilisation_of_tranche: function (frm) {
        let total_tranches = frm.doc.tranche_table ? frm.doc.tranche_table.length : 0;
        let total_tranche_amount_utilised = 0;
        let total_grant_amount = frm.doc.total_grant_amount || 0;
        if (total_tranches > 0) {

            total_tranche_amount_utilised = frm.doc.tranche_table.reduce((sum, row) => sum + (row.total_tranche_expenditure || 0), 0);

        }
        frm.set_value("total_grant_amount_utilised", total_tranches > 0 ? total_tranche_amount_utilised : 0);
        frm.set_value("total_tranche_amount_utilised", total_tranches > 0 ? (total_tranche_amount_utilised / total_grant_amount) * 100 : 0);
    },

    calculate_total_tranche_amount: function (frm) {
        let total_tranches = frm.doc.tranche_table ? frm.doc.tranche_table.length : 0;
        let total_tranche_amount_received = 0;
        if (total_tranches > 0) {
            total_tranche_amount_received = frm.doc.tranche_table.reduce((sum, row) => {
                if (row.tranche_status === "Received - On Time" || row.tranche_status === "Received - Delayed") {
                    return sum + (row.tranche_amount || 0);
                }
                return sum;
            }, 0);
        }
        frm.set_value("total_tranche_amount_received", total_tranches > 0 ? total_tranche_amount_received : 0);
    },

    progress_bar: function (frm) {
        let tranche_expenditure = frm.doc.total_tranche_amount_utilised || 0;
        let total_tranche_amount_received = frm.doc.total_tranche_amount_received || 0;
        let total_grant_amount = frm.doc.total_grant_amount || 0;
        let total_grant_received_percentage = total_grant_amount > 0 ? (total_tranche_amount_received / total_grant_amount) * 100 : 0;
        frm.dashboard.clear_headline();
        let excessProgress = total_grant_received_percentage > 100 ? total_grant_received_percentage - 100 : 0;
        let excessExpenditure = tranche_expenditure > 100 ? tranche_expenditure - 100 : 0;

        let html = `
        <div class="progress" style="height: 10px;">
            <div class="progress-bar bg-success" role="progressbar"
                 style="width:${parseFloat((total_grant_received_percentage).toFixed(2))}%;"
                 aria-valuenow="${total_grant_received_percentage}" aria-valuemin="0" aria-valuemax="100">
            </div>
            ${excessProgress > 0 ? `
            <div class="progress-bar bg-danger" role="progressbar"
                 style="width: ${parseFloat((excessProgress).toFixed(2))}%; ">
            </div>` : ''}
        </div>
        <p style="margin-top:5px;">
            <strong>Total Grant Received:</strong>
            <span style="color: ${total_grant_received_percentage > 100 ? 'red' : 'black'};"> ${parseFloat((total_grant_received_percentage).toFixed(2))}%</span>
        </p>

        <div class="progress" style="height: 10px;">
            <div class="progress-bar bg-warning" role="progressbar"
                 style="width: ${parseFloat((tranche_expenditure).toFixed(2))}%;"
                 aria-valuenow="${parseFloat((tranche_expenditure).toFixed(2))}" aria-valuemin="0" aria-valuemax="100">
            </div>
            ${excessExpenditure > 0 ? `
            <div class="progress-bar bg-danger" role="progressbar"
                 style="width: ${parseFloat((excessExpenditure).toFixed(2))}%; ">
            </div>` : ''}
        </div>
        <p style="margin-top:5px;">
    <strong>Total Grant Utilised:</strong>
    <span style="color: ${tranche_expenditure <= 100 ? 'Green' : 'red'};">
         ${parseFloat((tranche_expenditure).toFixed(2))}%
    </span>
     ${excessExpenditure > 0 ? `<strong>Over Utilisation:</strong>
    <span style="color: ${tranche_expenditure > 100 ? 'red' : 'black'};">
        ${parseFloat((tranche_expenditure - 100).toFixed(2))}%
    </span>` : ''}

</p>
<p>
    <strong>Calculation Formula:</strong><br>
    <span class="text-muted">
        Total Grant Received % = (Total Tranche Amount Received / Total Grant Amount) * 100
    </span>
    <br>
    <span class="text-muted">
        Total Grant Utilised % = (Total Tranche wise expense / Total Grant Amount) * 100
    </span>
</p>
    `;




        frm.fields_dict["tranche_progress_bar"].$wrapper.html(html);
    },

    check_total_tranche_amount: function (frm) {
        let total_tranche_amount = 0;

        frm.doc.tranche_table.forEach(row => {
            total_tranche_amount += row.tranche_amount;
        });

        if (total_tranche_amount > frm.doc.total_grant_amount) {
            // Show alert message
            frappe.msgprint({
                message: "Total Tranche Amount cannot be greater than Total Grant Amount",
                title: __('Alert'),
                indicator: 'yellow',
            });

            // Prevent form submission
            frappe.validated = false;

            // Set error message in description
            frm.set_df_property("total_grant_amount", "description",
                `<span style="color:red;">⚠ Total Tranche Amount exceeds the Total Grant Amount.</span>`);

            // Focus cursor on the total_grant_amount field
            frm.fields_dict["total_grant_amount"].set_focus();
        } else {
            // Clear error message if values are correct
            frm.set_df_property("total_grant_amount", "description", "");
        }
    }


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
    tranche_status: function (frm, cdt, cdn) {
        // if tranche_status is Received - On Time or Received - Delayed,  the Tranche_amount for that row should not be zero
        // and show a message if the amount is zero
        let row = locals[cdt][cdn];
        const allowedStatuses = ["Received - On Time", "Received - Delayed"];
        if (allowedStatuses.includes(row.tranche_status) && row.tranche_amount === 0) {
            frappe.validated = false;
            frappe.msgprint("Tranche Amount cannot be zero for Received - On Time or Received - Delayed status");
        }

    },

    due_date: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        // return error if start date and end date are not set
        if (!frm.doc.grant_agreement_start_date) {
            //clear the due_date filed in the child table
            row.due_date = null;
            //prevent saving the form
            frappe.validated = false;
            //focus the cursor on the grant agreement start date field
            frm.fields_dict["grant_agreement_start_date"].set_focus();
        }
        else if (!frm.doc.grant_agreement_end_date) {
            //clear the due_date filed in the child table
            row.due_date = null;
            //prevent saving the form
            frappe.validated = false;
            //focus the cursor on the grant agreement start date field
            frm.fields_dict["grant_agreement_end_date"].set_focus();
        }
        // Due Date should not be before Grant Agreement Start Date and it should not be after Grant Agreement End Date

        else if (row.due_date < frm.doc.grant_agreement_start_date) {
            //clear the due_date filed in the child table
            row.due_date = null;
            frappe.validated = false;
            frappe.msgprint("Due Date cannot be before Grant Agreement Start Date");
            //focus the cursor on the due date field in the child table
            frm.fields_dict["due_date"].set_focus();
        }
        else if (row.due_date > frm.doc.grant_agreement_end_date) {
            row.due_date = null;
            frappe.msgprint("Due Date cannot be after Grant Agreement End Date");
            frm.fields_dict["due_date"].set_focus();
            frappe.validated = false;
        }
        frappe.call({
            method: "funder_management_system.funder_management_system.doctype.financial_year.financial_year.save_financial_year",
            args: {
                fiscal_year: getFinancialYear(row.due_date)
            },
            callback: function (r) {
                if (r.message) {
                    row.tranche_financial_year = r.message;
                }
            }
        });
    },

});
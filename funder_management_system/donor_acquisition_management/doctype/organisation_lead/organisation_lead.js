frappe.ui.form.on("Organisation Lead", {
    onload_post_render: function(frm) {
        frm.trigger("lead_description");
        
    },

    before_save: function (frm) {
        frm.trigger("save_lead_history");
    },
    refresh: function (frm) {
        frm.get_field("table_lead_history").grid.cannot_add_rows = true;
        frm.trigger("load_compliance_checklist");
        
    },

    organisation_name: function (frm) {
        if (!frm.doc.organisation_name) {
            frm.refresh_field("website_url");
        }
    },
    lead_description: function (frm) {
        let descriptions = {
            "New Lead": "No outreach has happened to the lead for the current financial year.",
            "Warm Lead": "Exploration call or some reach out done for the financial year. Lead seems interested to proceed further.",
            "Hot Lead": "The proposal deck has been shared with the lead for the financial year. High probability of lead conversion.",
            "Confirmed Lead": "The lead has accepted the proposal and the MoU is signed.",
            "Cold Lead": "Lead did not respond/Lead stopped responding",
            "Dropped Lead": "Lead followups dropped from either side ",
        };

        let selected_stage = frm.doc.lead_stage;
        if(selected_stage === "Confirmed Lead"){
            //frm.set_df_property("lead_stage", "read_only", 1);
        }
        let description = descriptions[selected_stage] || "Select a lead stage to see details.";
        frm.set_df_property("lead_stage", "description", description);

    },

    lead_stage: function (frm) {

        
         if (!frm.doc.lead_name) {

            if (frm.doc.lead_stage == "Confirmed Lead") {
                frappe.msgprint({
                    title: __("Please Create a Organisation Lead"),
                    message: __("Please select the organisation name and save it before changing the Lead Stage to <strong>Confirmed Lead</strong>"),
                    indicator: "red"
                });
                frm.set_value("lead_stage", "New Lead");
            }
            
            return ; 
        }
        frm.trigger("lead_description");
        //check if organisation field is empty 
        if (frm.doc.lead_stage === "Confirmed Lead") {
            
            frappe.confirm(
                'Changing the Lead Status to "Confirmed Lead" for <strong>' + frm.doc.lead_name + `</strong> will create a new Donor record. <br> Do you want to proceed with this step? <br><hr> Click <strong>Yes</strong>: Create Donor <br><hr> Click <strong>No</strong>: Cancel and review the lead details.`,
                () => {
                    frappe.call({
                        method: "funder_management_system.donor_acquisition_management.doctype.organisation_lead.organisation_lead.create_donor_from_lead",
                        args: {
                            lead_name: frm.doc.name, // Pass only the name instead of full document
                        },
                        callback: function (r) {
                            if (r.message === true) {
                                

                                // Save the Organisation Lead only if donor creation succeeds
                                frm.save()
                                    .then(() => {
                                        frappe.msgprint(__('Donor created successfully!'));
                                    })
                                    .catch(() => {
                                        frappe.msgprint(__('Failed to save lead.'));
                                        frm.reload_doc(); // Reload if saving fails
                                    });
                            } else {
                                frappe.msgprint(__('Failed to create donor.'));
                                frm.reload_doc(); // Reload if donor creation fails
                            }
                        }
                    });
                },
                () => {
                    frappe.msgprint(__('Lead confirmation cancelled.'));
                    frm.reload_doc(); // Reload if user cancels
                }
            );
        }
    },  


    load_compliance_checklist: function (frm) {
        if (frm.is_new()) {  // Only load checklist if the document is already created
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Compliance Checklist",
                    fields: ["compliance_name"],
                },
                callback: function (r) {
                    if (r.message) {
                        frm.clear_table("compliance_checklist");
                        r.message.forEach((item) => {
                            let row = frm.add_child("compliance_checklist");
                            row.compliance_name = item.compliance_name;
                        });
                        frm.refresh_field("compliance_checklist");
                    }
                }
            });
        }
    },
    save_lead_history: function (frm) {
        // fetch the source_of_connection, thematic_areas lead_stage, financial_year and lead_category and save it to the Lead History child table
        let { lead_stage, financial_year, lead_category, disposition_note } = frm.doc;

        // if the child table is empty then add a new row with data
        if (frm.doc.table_lead_history.length === 0) {
            let lead_history = frm.add_child("table_lead_history");
            lead_history.lead_stage = lead_stage;
            lead_history.financial_year = financial_year;
            lead_history.lead_category = lead_category;
            lead_history.note = disposition_note;   
        }
        // if child table is not empty then check the lead stage and financial year and lead category if there is any change then add a new row with data
        else {
            let last_lead_history = frm.doc.table_lead_history[frm.doc.table_lead_history.length - 1];
            if (lead_stage !== last_lead_history.lead_stage || financial_year !== last_lead_history.financial_year || lead_category !== last_lead_history.lead_category || disposition_note !== last_lead_history.note) 
                {
                let lead_history = frm.add_child("table_lead_history");
                lead_history.lead_stage = lead_stage;
                lead_history.financial_year = financial_year;
                lead_history.lead_category = lead_category;
                lead_history.note = disposition_note;
            }
        }
        
        
    }
});

frappe.ui.form.on("Organisation Lead", {
    onload_post_render: function(frm) {
        frm.trigger("lead_description");
    },
    refresh: function (frm) {
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
            frm.set_df_property("lead_stage", "read_only", 1);
        }
        let description = descriptions[selected_stage] || "Select a lead stage to see details.";
        frm.set_df_property("lead_stage", "description", description);

    },

    lead_stage: function (frm) {
        
         if (!frm.doc.organisation_name) {
            frappe.msgprint({
                title: __("Please Create a Organisation Lead"),
                message: __("Please select the organisation name and save it before changing the Lead Stage."),
                indicator: "red"
            });
            return;
        }
        frm.trigger("lead_description");
        //check if organisation field is empty 
        if (frm.doc.lead_stage === "Confirmed Lead") {
            
            frappe.confirm(
                'Changing the Lead Status to "Confirmed Lead" for ' + frm.doc.lead_name + ` will create a new Donor record. \n Do you want to proceed with this step? \n\n Yes: Create Donor \n No: Cancel and review the lead details.`,
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
    }
});

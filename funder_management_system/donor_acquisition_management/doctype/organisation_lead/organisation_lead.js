frappe.ui.form.on("Organisation Lead", {
    // ✅ Ensures descriptions are loaded once the form is rendered
    onload_post_render: function (frm) {
        frm.trigger("lead_description");
    },
    onload: function (frm) {
        if (frm.is_new()) {
            frm.trigger("fetch_compliance_checklist");
        }
    },

    before_save: function (frm) {
        frm.trigger("save_lead_history");
    },

    refresh: function (frm) {
        frm.get_field("table_lead_history").grid.cannot_add_rows = true;
        frm.refresh_field("table_lead_history");

    },

    // Ensures website URL is refreshed if organisation name is removed
    organisation_name: function (frm) {
        if (!frm.doc.organisation_name) {
            frm.refresh_field("website_url");
        }
    },

    // Optimized Lead Description Logic
    lead_description: function (frm) {
        const descriptions = {
            "New Lead": "No outreach has happened to the lead for the current financial year.",
            "Warm Lead": "Exploration call or some reach out done for the financial year. Lead seems interested to proceed further.",
            "Hot Lead": "The proposal deck has been shared with the lead for the financial year. High probability of lead conversion.",
            "Confirmed Lead": "The lead has accepted the proposal and the MoU is signed.",
            "Cold Lead": "Lead did not respond/Lead stopped responding",
            "Dropped Lead": "Lead followups dropped from either side",
        };

        frm.set_df_property("lead_stage", "description", descriptions[frm.doc.lead_stage] || "Select a lead stage to see details.");
    },

    // ✅ Lead Stage Logic - Prevents unnecessary execution
    lead_stage: function (frm) {
        if (!frm.doc.lead_name && frm.doc.lead_stage === "Confirmed Lead") {
            frappe.msgprint({
                title: __("Please Create an Organisation Lead"),
                message: __("Please select the organisation name and save it before changing the Lead Stage to <strong>Confirmed Lead</strong>"),
                indicator: "red"
            });
            frm.set_value("lead_stage", "New Lead");
            return;
        }

        frm.trigger("lead_description");

        if (frm.doc.lead_stage === "Confirmed Lead") {
            frappe.confirm(
                `Changing the Lead Status to "Confirmed Lead" for <strong>${frm.doc.lead_name}</strong> will create a new Donor record. <br>
                Do you want to proceed with this step? <br><hr> 
                Click <strong>Yes</strong>: Create Donor <br><hr> 
                Click <strong>No</strong>: Cancel and review the lead details.`,
                () => {
                    frappe.call({
                        method: "funder_management_system.donor_acquisition_management.doctype.organisation_lead.organisation_lead.create_donor_from_lead",
                        args: { lead_name: frm.doc.name },
                        callback: function (r) {
                            if (r.message) {
                                frappe.msgprint(__('Donor created successfully!'));
                                frm.reload_doc();
                            } else {
                                frappe.msgprint(__('Failed to create donor.'));
                                frm.reload_doc();
                            }
                        }
                    });
                },
                () => {
                    frappe.msgprint(__('Lead confirmation cancelled.'));
                    frm.reload_doc()
                }
            );
        }
    },

    fetch_compliance_checklist: function (frm) {
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Compliance Checklist",
                fields: ["compliance_name"],
            },
            callback: function (r) {
                if (r.message && frm.is_new()) {
                    frm.clear_table("compliance_checklist");
                    r.message.forEach((item) => {
                        let row = frm.add_child("compliance_checklist");
                        row.compliance_name = item.compliance_name;
                    });
                    frm.refresh_field("compliance_checklist");
                }
            }
        });
    },

    // ✅ Lead History Optimization - Avoids unnecessary API calls
    save_lead_history: function (frm) {
        let { lead_stage, financial_year, lead_category, disposition_note } = frm.doc;
        let existing_stages = (frm.doc.table_lead_history || []).map(row => row.lead_stage);

        if (!existing_stages.includes(lead_stage)) {
            let lead_history = frm.add_child("table_lead_history");
            Object.assign(lead_history, { lead_stage, financial_year, lead_category, note: disposition_note });

            frm.refresh_field("table_lead_history");
            frm.dirty(true);
            frm.save()
        }
    }
});

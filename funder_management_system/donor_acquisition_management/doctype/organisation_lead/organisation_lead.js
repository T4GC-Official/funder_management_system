frappe.ui.form.on("Organisation Lead", {
    // ✅ Ensures descriptions are loaded once the form is rendered
    onload_post_render: function (frm) {
        frm.trigger("lead_description");
        frm.trigger("update_lead_stage_dropdown_options");
        console.log("Onload Post Render Triggered");
    },
    onload: function (frm) {
        if (frm.is_new()) {
            frm.trigger("fetch_compliance_checklist");
        }
    },

    before_save: function (frm) {
        frm.trigger("save_lead_history");
    },
    after_save: function (frm) {
        frm.trigger("update_lead_stage_dropdown_options");
        console.log("After Save Triggered");
    },
    refresh: function (frm) {
        frm.get_field("table_lead_history").grid.cannot_add_rows = true;
        frm.refresh_field("table_lead_history");
        // Add button inside the large text field
        // frm.fields_dict.disposition_note.$wrapper.append(`
        //     <button class="btn btn-sm btn-primary enhance-text-btn" 
        //         style="margin-top: 5px;">Enhance Note</button>
        // `);

        // // Add click event to the button
        // frm.fields_dict.disposition_note.$wrapper.find('.enhance-text-btn').click(function() {
        //     let text = frm.doc.disposition_note || "";
        //     let enhanced_text = enhance_text_function(text); // Call enhancement function
        //     frm.set_value("disposition_note", enhanced_text);
        // });

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
                                if (r.message.status === "success") {
                                    frappe.show_alert({
                                        message: __("Donor created successfully!"),
                                        indicator: "green"
                                    });
                    
                                    frm.set_value("lead_stage", "Confirmed Lead");
                                    frm.save();                    
        
        
                                }
        
                                else if (r.message.status === "duplicate") {
                                    frappe.msgprint(__('Donor already exists! Reloading...'));
                                    frm.reload_doc();  
                                } 
                                else {
                                    frappe.msgprint(__('Failed to create donor.'));
                                    frm.reload_doc();
                                }
                            }
                        }
                    });
                },
                () => {
                    frappe.msgprint(__('Lead confirmation cancelled.'));
                    frm.reload_doc();
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

       save_lead_history: function (frm) {
        let { lead_stage, financial_year, lead_category, disposition_note } = frm.doc;
        let existing_stages = (frm.doc.table_lead_history || []).map(row => row.lead_stage);

        let last_lead_history = frm.doc.table_lead_history?.slice(-1)[0];
        console.log("Last Lead History:", last_lead_history);
        console.log("Current Lead Stage:", lead_stage);
        if (last_lead_history?.lead_stage !== lead_stage) {
            let lead_history = frm.add_child("table_lead_history");
            Object.assign(lead_history, { lead_stage, financial_year, lead_category, note: disposition_note });
            frm.refresh_field("table_lead_history");
            frm.trigger("update_lead_stage_dropdown_options");
            console.log("Lead History Updated:", lead_history);
            frm.dirty(true);
            frm.save();
        }
    },
    update_lead_stage_dropdown_options: function (frm) {

        let existing_stages = (frm.doc.table_lead_history || []).map(row => row.lead_stage);
        
        if (existing_stages.includes("New Lead")) {
            frm.set_df_property("lead_stage", "options", [
                "Warm Lead",
                "Hot Lead",
                "Confirmed Lead",
                "Cold Lead",
                "Dropped Lead"
            ]);
        } 
        if (frm.doc.lead_stage === "New Lead") {
            frm.set_df_property("lead_stage", "options", [
                "New Lead",
                "Warm Lead",
                "Hot Lead",
                "Confirmed Lead",
                "Cold Lead",
                "Dropped Lead"
            ]);
        }
    }
});
function enhance_text_function(text) {
    console.log("Enhancing text:", text);
    //return "**Enhanced:** " + text.toUpperCase(); // Example: Converts to uppercase and adds prefix
    const data = { text };
    return fetch("http://127.0.0.1:11434/api/generate", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        const reader = response.body.getReader();
        const stream = new ReadableStream({
            async *[Symbol.asyncIterator]() {
                let result;
                while (!(result = await reader.read()).done) {
                    yield result.value;
                }
            }
        });
        const decoder = new TextDecoder("utf-8");
        const streamReader = stream.pipeThrough(new TransformStream({
            transform(chunk, controller) {
                controller.enqueue(decoder.decode(chunk));
            }
        }));
        return new Response(streamReader).text();
    })
    .then(text => {
        const responses = text.split(/{"model":"DeepSeek-R1:latest","created_at":"[0-9TZ:-]+"}/);
        const finalResponse = responses[responses.length - 1];
        return finalResponse;
    })
    .catch(error => {
        console.error("Error:", error);
        return text;
    });
}
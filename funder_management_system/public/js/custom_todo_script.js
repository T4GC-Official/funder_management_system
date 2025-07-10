frappe.ui.form.on("ToDo", {
    onload(frm) {
        if (frappe.session.user !== 'Administrator') {
            console.log(frappe.session.user);
            frm.set_df_property('role', 'hidden', 1);
            frm.set_df_property('reference_type', 'hidden', 1);
            frm.set_df_property('reference_name', 'hidden', 1);
            frm.set_df_property('assignment_rule', 'hidden', 1);
            frm.set_df_property('color', 'hidden', 1);
            if(frm.is_new()) {
            frm.set_value('assigned_by', frappe.session.user);
            frm.set_df_property('assigned_by', 'read_only', 1);
            }

        }
    }
});
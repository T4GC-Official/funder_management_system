frappe.ui.form.on("ToDo", {
    onload(frm) {
        if (frappe.session.user !== 'Administrator') {
            frm.set_df_property('role', 'hidden', 1);
            frm.set_df_property('reference_type', 'hidden', 1);
            frm.set_df_property('reference_name', 'hidden', 1);
            frm.set_df_property('assignment_rule', 'hidden', 1);
        }}
});
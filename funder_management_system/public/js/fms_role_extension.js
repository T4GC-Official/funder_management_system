frappe.ui.form.on("Role Profile", {
	refresh: function (frm) {
		// Allow Fundraising Admin to manage role profiles
		if (has_common(frappe.user_roles, ["Administrator", "System Manager", "Fundraising Admin"])) {
			if (!frm.roles_editor) {
				const role_area = $(frm.fields_dict.roles_html.wrapper);
				frm.roles_editor = new frappe.RoleEditor(role_area, frm);
			}
			frm.roles_editor.show();
		}
	},

	validate: function (frm) {
		if (frm.roles_editor) {
			frm.roles_editor.set_roles_in_table();
		}
	},
});

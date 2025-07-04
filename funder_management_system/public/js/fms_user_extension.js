frappe.provide('fms');

frappe.ui.form.on('User', {
    async onload(frm) {
        frm.can_edit_roles = has_access_to_edit_user();

        // Fetch FMS modules before anything else
        const response = await frappe.call('funder_management_system.utils.get_fms_modules');
        const fms_modules = response.message || [];
        frm.doc.__onload.all_modules = fms_modules;

        if (frm.is_new() && frm.roles_editor) {
            frm.roles_editor.reset();
        }

        if (
            frm.can_edit_roles &&
            !frm.is_new() &&
            ["System User", "Website User"].includes(frm.doc.user_type)
        ) {
            if (!frm.roles_editor) {
                const role_area = $('<div class="role-editor">').appendTo(frm.fields_dict.roles_html.wrapper);
                frm.roles_editor = new frappe.RoleEditor(role_area, frm, frm.doc.role_profiles && frm.doc.role_profiles.length ? 1 : 0);

                if (frm.doc.user_type == "System User") {
                    const module_area = $('<div>').appendTo(frm.fields_dict.modules_html.wrapper);
                    frm.module_editor = new frappe.ModuleEditor(frm, module_area);
                }
            } else {
                frm.roles_editor.show();
            }
        }
    }
});

function has_access_to_edit_user() {
    return has_common(frappe.user_roles, get_roles_for_editing_user());
}

function get_roles_for_editing_user() {
    return (
        frappe
            .get_meta("User")
            .permissions.filter((perm) => perm.permlevel >= 1 && perm.write)
            .map((perm) => perm.role) || ["Fundraising Admin"]
    );
}

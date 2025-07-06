frappe.listview_settings['Dashboard List'] = {
    button: {
        show(doc) {
            return true;
        },
        get_label() {
            return "View Dashboard";
        },
        get_description(doc) {
            return `Open dashboard: ${doc.dashboard}`;
        },
        action(doc) {
            frappe.set_route(`/app/${encodeURIComponent(doc.dashboard)}`);
        }
    }
};

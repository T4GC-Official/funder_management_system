frappe.listview_settings['Report'] = {
    get_indicator(doc) {
        return null;
    },

    // Add "View Report" button after ID (for non-Administrators only)
    button: {
        show(doc) {
           return true;
        },
        get_label() {
            return "View Report";
        },
        get_description(doc) {
            return `Open ${doc.name} as report`;
        },
        action(doc) {
            const route = `/app/query-report/${encodeURIComponent(doc.name)}`;
            frappe.set_route(route);
        }
    }
};

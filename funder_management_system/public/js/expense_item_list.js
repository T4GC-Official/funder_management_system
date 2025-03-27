frappe.listview_settings['Expense Item'] = {
    refresh: function (frm) {
        document.querySelector('button[data-label="Add Expense Item"]').style.display = 'none';
        document.querySelectorAll('button').forEach(button => {
            if (button.textContent.trim() === "Create a new Expense Item") {
                button.style.display = 'none';
            }
            if (button.textContent.trim() === "Create your first Expense Item") {
                button.style.display = 'none';
            }
        });

    }
};

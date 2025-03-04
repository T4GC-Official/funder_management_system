// Run after Frappe UI is fully loaded
frappe.ui.toolbar.add_help = function () {
    console.log("Help menu disabled.");
};

// Remove Help menu & vertical separator from the navbar
$(document).ready(() => {
    $(".dropdown-help").remove();  // Removes the Help dropdown
    $(".navbar .vertical-bar").remove();  // Removes the vertical separator
});

document.addEventListener("DOMContentLoaded", function () {
    // Function to remove "Framework" from the sidebar
    function removeFrameworkApp() {
        document.querySelectorAll(".app-item").forEach(item => {
            let appName = item.getAttribute("data-app-name");
            let appTitle = item.querySelector(".app-item-title");

            if (appName === "frappe" || (appTitle && appTitle.innerText.trim() === "Framework")) {
                item.remove();
                console.log("Framework removed from sidebar.");
            }
        });
    }

    // Run once after a delay (for initial load)
    setTimeout(removeFrameworkApp, 1000);

    // Watch for changes in the sidebar (handles dynamic loading)
    let sidebarObserver = new MutationObserver(() => {
        removeFrameworkApp();
    });

    let sidebar = document.querySelector(".sidebar");
    if (sidebar) {
        sidebarObserver.observe(sidebar, { childList: true, subtree: true });
    }
});




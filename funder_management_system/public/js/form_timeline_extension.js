document.addEventListener("DOMContentLoaded", function () {
	function removeActionButtons() {
		document.querySelectorAll(".btn").forEach(button => {
			const btnText = button.innerText.trim();
			if (btnText === "New Email" || btnText === "New Event") {
				button.remove();
			}
		});
	}

	// Observe changes in the timeline header
	const observer = new MutationObserver(removeActionButtons);
	observer.observe(document.body, {
		childList: true,
		subtree: true
	});

	// Initial cleanup
	removeActionButtons();
});

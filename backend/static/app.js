document.querySelectorAll(".delete-form").forEach((form) => {
    form.addEventListener("submit", (event) => {
        const confirmed = window.confirm("Delete this event? Related records must be removed first.");
        if (!confirmed) {
            event.preventDefault();
        }
    });
});

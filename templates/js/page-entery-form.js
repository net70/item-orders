function submitForm() {
    // Validate the form fields
    const firstName = document.getElementById("first_name").value;
    const lastName = document.getElementById("last_name").value;
    const email = document.getElementById("email").value;

    if (!firstName || !lastName || !email) {
        alert("All fields are mandatory. Please fill them out.");
        return;
    }

    // Assuming validation is successful, hide the prompt
    document.getElementById("prompt-modal").style.display = "none";
}
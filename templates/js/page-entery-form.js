// add data to localstorage
const order = {
    'user_id': undefined,
    'first_name': undefined,
    'last_name': undefined,
    'email': undefined,
    'items': [],
    'total_cost': 0,
    'amount_paid': 0,
    'coupon_code': undefined,
    'discount': 0
  };

function submitEntryForm() {
    // Validate the form fields
    const firstName = document.getElementById("first_name").value;
    const lastName = document.getElementById("last_name").value;
    const email = document.getElementById("email").value;
  
    if (!firstName || !lastName || !email) {
        alert("All fields are mandatory. Please fill them out.");
        return;
    }
  
    order['first_name'] = firstName;
    order['last_name'] = lastName;
    order['email'] = email;
  
    // Assuming validation is successful, hide the prompt
    document.getElementById("prompt-modal").style.display = "none";
  }
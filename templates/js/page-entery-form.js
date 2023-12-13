let order = undefined;


// TODO: add data to localstorage
function fetchSessionData() {
  let sessionData = localStorage.getItem('sessionData');

  if (!sessionData){
    // Make a request to fetch session data
    fetch('/get_session_data/', {
      method: 'GET',
      credentials: 'include'  // Include cookies in the request
    })
      .then((response) => {
        if (response.status === 200) {
          return response.json();
        } else {
          throw new Error('Failed to fetch session data.');
        }
      })
      .then((data) => {
        // Process the session data
        sessionData = data;
      })
      .catch((error) => {
        console.error('Error fetching session data:', error);
      });
  } else {
    sessionData = JSON.parse(sessionData);
  }

  if (!sessionData) {
    sessionData = {
      'user_id': undefined,
      'first_name': undefined,
      'last_name': undefined,
      'email': undefined,
      'cart': [],
      'total_cost': 0,
      'amount_paid': 0,
      'coupon_code': undefined,
      'discount': 0
    }
  }
  return sessionData;
}

order = fetchSessionData();

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
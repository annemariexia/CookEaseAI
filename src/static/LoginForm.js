document.addEventListener('DOMContentLoaded', function () {
  function handleSubmit(event) {
    event.preventDefault();

    var username = document.getElementById('username').value;
    var email = document.getElementById('email').value;
    var password = document.getElementById('password').value;
    

    var userData = {
      username: username,
      email: email,
      password: password
    }

    fetch('/verify', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(userData)
    })
    .then(response => response.json())
    .then(data => {
      console.log(data, data.status);  
      if (data.message === 'success') {
        window.location.href = '/input_goal/'+ username;
      }    
    })
    .catch(error => {
      console.error('Error:', error);
    });
  }

  var form = document.getElementById('login-form');
  form.addEventListener('submit', handleSubmit);
});

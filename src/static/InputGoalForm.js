document.addEventListener('DOMContentLoaded', function () {
  function handleSubmit(event) {
    event.preventDefault();

    var calorieGoal = document.getElementById('calorie-goal').value;
    var carbGoal = document.getElementById('carb-goal').value;
    var proteinGoal = document.getElementById('protein-goal').value;
    var fatGoal = document.getElementById('fat-goal').value;
    var email = document.getElementById('email').value;
    var username = document.getElementById('username').value;

    

    var goalData = {
      calorie_goal: calorieGoal,
      carb_goal: carbGoal,
      protein_goal: proteinGoal,
      fat_goal: fatGoal,
      email: email
    }


    console.log(goalData);

    fetch('/home', {
      method: 'POST', 
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(goalData)
    })
    .then(response => response.json())
    .then(data => {
      console.log(data, data.status);  
      if (data.message === 'success') {
        window.location.href = '/recipe/' + username;
      }    
    })
    .catch(error => {
      console.error('Error:', error);
    });
  }

  var form = document.getElementById('input-form');
  form.addEventListener('submit', handleSubmit);
});


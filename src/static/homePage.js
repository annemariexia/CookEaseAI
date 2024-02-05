import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import './style/homePage.css'




const Home = () => {
  const navigate  = useNavigate ();
  const [data, setData] = useState(null);
  const [buttonClicked, setButtonClicked] = useState(false);

  const handleButtonClick = () => {
    setButtonClicked(true);
  };


  useEffect(() => {
    const ingredientForm = document.getElementById("ingredientForm");

    const submitHandlerFunction = async (event) => {
      event.preventDefault();

      const recipeButton = document.getElementById("recipeButton");
      recipeButton.disabled = true;
      recipeButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';

      const formData = new FormData(event.target);

      try {
        const response = await fetch("http://localhost:5000/getIngredients", {
          method: "POST",
          body: formData,
        });

        console.log('Response:', response);

        if (response.ok) {
          const data = await response.json();
          setData(data);
          console.log(data);

        } else {
          throw new Error('Network response was not ok');
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        recipeButton.disabled = false;
        recipeButton.innerHTML = 'Get a delicious recipe!';
      }
    };

    // Attach the submit event listener to the form
    ingredientForm.addEventListener("submit", submitHandlerFunction);

    // Cleanup: Remove the event listener when the component unmounts
    return () => {
      ingredientForm.removeEventListener("submit", submitHandlerFunction);
    };
  }, []); 

  return (
    
    <div>
      <nav class="navbar navbar-expand-lg">
        <span class="navbar-brand mb-0 h1">  CookEaseAI  </span>
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarSupportedContent">
            <ul class="navbar-nav mr-auto">
                <li class="nav-item active">
                    <a class="nav-link" href="/home">Home <span class="sr-only">(current)</span></a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="view_nutrition_info">View Nutrition Info</a>
                </li>
            </ul>
            <ul class="navbar-nav ml-auto">
                <li class="nav-item dropdown"> 
                    <a class="nav-link dropdown-toggle welcome-user" href="#" id="navbarDropdown" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                        Welcome, !
                    </a>
                    <div class="dropdown-menu" aria-labelledby="navbarDropdown">
                        <a class="dropdown-item" href="#">Setting</a>
                        <a class="dropdown-item" href="#">Another action</a>
                        <div class="dropdown-divider"></div>
                        <a class="dropdown-item" href="#">Logout</a>
                    </div>
                </li>
            </ul>
        </div>
    </nav>

      <div class="main-container">
              <div class="row" style={{ paddingTop: '20px' }}>
                  <div>
                      <div class="form-container">
                          <form id="ingredientForm" class={`${buttonClicked ? 'form-container-clicked' : 'form-container-1'}`} action="/getIngredients" method="POST">
                              <div class="form-group">
                                  <label for="ingredients">Enter the ingredients you have:</label>
                                  <input type="text" class="form-control input-text" id="ingredients" name="ingredients" autocomplete="off" placeholder="salmon fillet, ground beef, pork chop..."/>
                              </div>
                              <div class="form-group">
                                  <label for="cuisine">Enter the cuisine you want:</label>
                                  <input type="text" class="form-control input-text" id="cuisine" name="cuisine" autocomplete="off" placeholder="italian, japanese, new american..."/>
                              </div>
                              <div class="form-group">
                                  <label for="foodType">Select a Food Type:</label>
                                  <select class="form-control" id="foodType" name="foodType">
                                      <option value="any">Any</option>
                                      <option value="appetizer">Appetizer</option>
                                      <option value="entree">Entree</option>
                                      <option value="dessert">Dessert</option>
                                  </select>
                              </div>
                              <div class="form-group">
                                  <label for="portions">Select the number of people:</label>
                                  <select class="form-control" id="portions" name="portions">
                                      <option value="1">1</option>
                                      <option value="2">2</option>
                                      <option value="3">3</option>
                                      <option value="4+">4+</option>
                                  </select>
                              </div>
                              <div class="form-group">
                                  <label for="allergens">Allergens/Ingredients to avoid:</label>
                                  <input type="text" class="form-control input-text" id="allergens" autocomplete="off" name="allergens" placeholder="tree nuts, gluten..."/>
                              </div>


                              <button type="submit" class="btn btn-primary" id="recipeButton" onClick={handleButtonClick} >Get a delicious recipe!</button>


                          </form>
                      </div>
                  </div>

                  <div>                 
                    <div id="recipeImage" class="recipe-container">
                      {data && Array.isArray(data) ? (
                        data.map((recipe, index) => (
                          <div className="recipe-item-container" key={index}>
                            <img src={`${recipe.image_url}`} />
                            <p>{recipe.recipe_name}</p>
                            <p>
                              Calories: {Math.round(recipe.nutrient_info["calories"])} Protein:{" "}
                              {Math.round(recipe.nutrient_info["protein"])} Carbohydrates:{" "}
                              {Math.round(recipe.nutrient_info["carbs"])} 
                            </p>
        
                            <Link
                              to={
                                 '/recipe_page'
                              }
                              state= {{
                                recipeText: encodeURIComponent(recipe.recipe_text),
                                calories: encodeURIComponent(recipe.nutrient_info['calories']),
                                protein: encodeURIComponent(recipe.nutrient_info['protein']),
                                fat: encodeURIComponent(recipe.nutrient_info['fat']),
                                carbs: encodeURIComponent(recipe.nutrient_info['carbs']),
                              }}>
                              <button type="button" className="btn btn-view">
                                {'>'} View Recipe
                              </button>
                            </Link>
                          </div>
                        ))
                      ) : (
                        <>
                        </>
                          
                      )}
                    </div>
                  </div>
            </div>
        </div>
    </div>
  );
};


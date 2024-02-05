import React from 'react';
import { useLocation } from 'react-router-dom';
import './style/recipePage.css'


const RecipePage = () => {
    const location = useLocation();
    console.log("Location:", location);
    console.log("Location state:", location.state);
    const { recipeText, calories, protein, fat, carbs } = location.state || {};
    console.log('Recipe Data:', recipeText, calories, protein, fat, carbs);
    // const recipeText = "Apple-Orange Cobbler:\nIngredients:\n- 2 large apples\n- 2 large oranges\n- 1 cup all-purpose flour\n- 1/4 teaspoon baking powder\n- 1/4 teaspoon ground cinnamon\n- 1/2 teaspoon salt\n- 1/2 cup melted butter\n- 1/4 cup plus 2 tablespoons white sugar\n- 2/3 cup orange juice\n\nInstructions:\n1. Preheat oven to 375 F/190 C and prepare a 9 x 9 inch pan by greasing and lightly flouring with all-purpose flour.\n2. Peel apples and oranges and chop into small pieces. Place in a large mixing bowl.\n3. In a smaller bowl, combine the flour, baking powder, cinnamon, salt, butter, and sugar until a crumbly consistency is formed and all the ingredients are evenly distributed.\n4. Pour the orange juice over the chopped fruit in the larger bowl and stir until the fruit is evenly coated.\n5. Evenly spread the chopped fruit in the prepared pan.\n6. Sprinkle the flour mixture over the fruit, covering it completely.\n7. Bake for 30-35 minutes or until the top is golden brown and the fruit is bubbling.\n8. Allow to cool slightly before serving.";
    // console.log("reicpe text: ",recipeText);
    // console.log("portions:", portions);
    const recipeInfo = decodeURIComponent(recipeText)
    console.log("recipe info:", recipeInfo);
    const lines = recipeInfo.split('Instructions:');
    var ingredients = lines[0];
    const ingredients_list = ingredients.split('Ingredients:');
    const recipeName = ingredients_list[0];
    const instructions = lines[1].split('\n');
    ingredients = ingredients_list[1].split('\n');

    const handleSubmit = async (event) => {
        event.preventDefault();
      
        const headers = new Headers();
        headers.append('Content-Type', 'application/json');
        headers.append('Accept', 'application/json');
        headers.append('Access-Control-Allow-Origin', 'http://localhost:3000');
        headers.append('GET', 'POST', 'OPTIONS');
        // headers.append('User-id', user_id);
      
        console.log(headers);
        try {
          const response = await fetch('http://localhost:5000/recipe_page', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({
              calories: calories,
              protein: protein,
              fat: fat,
              carbs: carbs,
            }),
          });

          console.log('Response:', response);
          console.log('Response Text:', await response.text());
      
          if (response.ok) {
            console.log('Recipe submitted successfully.');
          } else {
            console.error('Failed to submit recipe', response.statusText);
          }
        } catch (error) {
          console.error('Error:', error);
        }
      }


  return (
    <div className="container">
      <h1>{recipeName}</h1>
      <h2>Ingredients:</h2>
      <ul>
        {ingredients.map((item, index) => (
          <p key={index}>{item.trim()}</p>
        ))}
      </ul>

      <h2>Instructions:</h2>
      <ol>
        {instructions.map((line, index) => (
          <p key={index}>{line.trim()}</p>
        ))}
      </ol>

      <div className="submit-form">
        <form action="/recipe_page" method="POST" class="recipe-form" onSubmit={ handleSubmit }>
          <input type="hidden" name="recipe_text" autocomplete="off" value={recipeText} />
          <input type="hidden" name="calories" autocomplete="off" value={calories} />
          <input type="hidden" name="protein" autocomplete="off" value={protein} />
          <input type="hidden" name="fat" autocomplete="off" value={fat} />
          <input type="hidden" name="carbs" autocomplete="off" value={carbs} />

          <label class="recipe-label">
            <input type="checkbox" id="cookCheckbox" name="cookCheckbox" /> Did you cook this recipe?
          </label>

          <button type="submit" className="submit-btn" id="addNutritionInfoBtn">
            Submit & Leave Page
          </button>
        </form>
      </div>
    </div>
  );
};

export default RecipePage;

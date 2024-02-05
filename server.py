from datetime import datetime
from flask import Flask, flash
from flask_cors import CORS, cross_origin
from flask import render_template
from flask import Response, request, jsonify, redirect, url_for, session, send_from_directory
from flask_pymongo import PyMongo
from flask_session import Session
from pymongo import MongoClient
import re
import os
import secrets
import openai
import API_keys
import requests
import json
import bcrypt
from base64 import b64decode
from pathlib import Path
from flask_oauthlib.client import OAuth, OAuthException
from dotenv import load_dotenv


load_dotenv()


application = Flask(__name__, static_url_path='/static', static_folder='src/static')

application.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
application.config['SESSION_TYPE'] = 'filesystem'
application.config["SESSION_COOKIE_SAMESITE"] = "None" # allows the session cookie to be sent with cross-origin requests
application.config["SESSION_COOKIE_SECURE"] = True


application.config["CLIENT_ID"] = os.getenv('CLIENT_ID')
application.config["CLIENT_SECRET"] = os.getenv('CLIENT_SECRET')



oauth = OAuth(application)
Session(application)


google = oauth.remote_app(
    'google',
    consumer_key=application.config.get('CLIENT_ID'),
    consumer_secret= application.config.get('CLIENT_SECRET'),
    request_token_params={
        'scope': 'email profile'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',

)

# Configure the Flask app to use PyMongo with the MongoDB URI
application.config["MONGO_URI"] = "mongodb+srv://annexxj:dVtMmJEcDQ4T0a3S@recipegeneratordb.jyr22t0.mongodb.net/?retryWrites=true&w=majority"
mongo = PyMongo(application)
CORS(application)

# Connect to your MongoDB database
client = MongoClient(
    "mongodb+srv://annexxj:dVtMmJEcDQ4T0a3S@recipegeneratordb.jyr22t0.mongodb.net/?retryWrites=true&w=majority",
    connectTimeoutMS=300000,
    socketTimeoutMS=300000,
    connect=True,
    maxPoolSize=200,
)

db = client.get_database("RecipeGeneratorDB")

openai.api_key = API_keys.SECRET_KEY
calorieNinjas_url = 'https://api.calorieninjas.com/v1/nutrition?query='
calorieNinjas_api_key = API_keys.CALORIENINJAS_KEY
apiNinja_api_key = API_keys.APININJA_KEY

application.secret_key = os.urandom(24)  # 24 bytes for a secure key
application.config['SECRET_KEY'] = application.secret_key


@application.route('/')
@cross_origin()
def index():
    if 'GOOGLE_TOKEN' in session:
        print(application.config.get('GOOGLE_USER_PROFILE'))
        return redirect(url_for('input_goal', username=session['username'], email=session['email']))
    return render_template("index.html")


@application.route('/login')
@cross_origin()
def google_login():
    return google.authorize(callback=url_for('authorized', _external=True))


@application.route('/logout')
@cross_origin()
def logout():
    session.pop('google_token', None)
    return redirect(url_for('index'))



@application.route('/login/authorized')
@cross_origin()
def authorized():
    resp = google.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (resp['access_token'], '')
    me = google.get('userinfo')  #family_name, id, locale, name, picture, verified_email
    application.config["USER_FNAME"] = me.data['given_name']
    application.config["USER_EMAIL"] = me.data['email']
    application.config["USER_ID"] = me.data['id']

    # add user to db
    user_data = {
        "username": me.data['given_name'],
        "email": me.data['email'],
        "password": None,
        "google_id": me.data['id'],
    }


    existing_user = db.users.find_one({"$or": [{"email": me.data['email']}]})
    if existing_user:
        try:
            result = db.users.insert_one(user_data)
            user_id = result.inserted_id  # Get the _id of the inserted user
            session['username'] = me.data['given_name']
            session['email'] = me.data['email']
            session['user_id'] = str(user_id)  # Convert ObjectId to string for session storage     

        except Exception as e:
            print(f"An error occurred: {str(e)}")
    else:
        user_data = {
                "username": me.data['given_name'],
                "email": me.data['email']
            }
        try:
            result = db.users.insert_one(user_data)
            user_id = result.inserted_id  # Get the _id of the inserted user
            print("input_goal:", user_id)
            session['username'] = me.data['given_name']
            session['email'] = me.data['email']
            session['user_id'] = str(user_id)  # Convert ObjectId to string for session storage

        except Exception as e:
            print(f"An error occurred: {str(e)}")

    return redirect(url_for('verify', user_fname=me.data['given_name'], user_email=me.data['email'], user_id=me.data['id']))

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')


@application.route('/verify', methods=['GET', 'POST'])
@cross_origin()
def verify():

    username = request.args.get('user_fname')
    email = request.args.get('user_email')

    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        bytes = password.encode('utf-8') 
        salt = bcrypt.gensalt() 
        hashed_password = bcrypt.hashpw(bytes, salt) 
    
        existing_user = db.users.find_one({"$or": [{"username": username}, {"email": email}]})
        if existing_user:
            stored_hashed_password = existing_user.get('password')
            userBytes = password.encode('utf-8') 
            result = bcrypt.checkpw(userBytes, stored_hashed_password) 
            print(result)

            if not result:
                return jsonify({'error': 'Invalid password'}), 401
            else:
                response = jsonify({"message": "success"})
                return response 
        
        else:
            user_data = {
                "username": username,
                "email": email,
                "password": hashed_password
            }
            try:
                result = db.users.insert_one(user_data)
                user_id = result.inserted_id  
                print("input_goal:", user_id)
                session['username'] = username
                session['email'] = email
                session['user_id'] = str(user_id) 
                response = jsonify({"message": "success", "user_id": str(user_id)})
                return response 

            except Exception as e:
                print(f"An error occurred: {str(e)}")
    
    return redirect(url_for('input_goal', username=username, email=email))


@application.route('/input_goal/<username>/<email>', methods=['GET'])
@cross_origin()
def input_goal(username, email):
    return render_template("input_goal.html", username=username, email=email)


@application.route('/home', methods=['GET', 'POST'])
@cross_origin()
def home():
    # print("Headers:", request.headers)
    # user_id = request.headers.get('User-id')
    # print("user id here:", user_id)
    if request.method == 'POST':
        data = request.get_json()
        calorie_goal = data.get('calorie_goal')
        carb_goal = data.get('carb_goal')
        protein_goal = data.get('protein_goal')
        fat_goal = data.get('fat_goal')
        email = data.get('email')

        if email:
            goal_data = {
            "calorie_goal": calorie_goal,
            "carb_goal": carb_goal,
            "protein_goal": protein_goal,
            "fat_goal": fat_goal,
            "email": email
        }

        try:
            db.goals.replace_one(
                {"email": email},   
                goal_data,              
                upsert=True         
            )
            response = jsonify({"message": "success"})
            return response
    
        except Exception as e:
            return jsonify({"error": f"Error adding goal data: {e}"}), 500

    return render_template('index.html')


@application.route('/recipe/<username>/', methods=['GET'])
@cross_origin()
def recipe(username):
    return render_template("home.html", username=username)


@application.route('/getIngredients', methods=['POST'])
@cross_origin()
def generate_recipes():
    ingredients = request.form.get('ingredients')
    cuisine = request.form.get('cuisine')
    foodType = request.form.get('foodType')
    portions = request.form.get('portions')
    allergens = request.form.get('allergens')


    print(ingredients)
    print(cuisine)
    print(foodType)

    three_recipes = []
    three_images = []
    three_names = []
    three_nutrition = []

    while len(three_names) != 3:
        prompt = f"Give me a {cuisine} {foodType} recipe in English for {portions} people that contains: {ingredients} but not {allergens}. Strictly follow the format: the recipe you provide should include a name, bullet points of ingredients under 'Ingredients:', and steps of instructions under 'Instructions:'. Keep tokens under 600."

        response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=600)
        recipe = response["choices"][0]["text"].strip()
        recipe_name = recipe.split('\n')[0]

        if recipe_name not in three_names and recipe_name.strip() != "Ingredient:":
            nutrients = {"calories":0, "fat":0, "protein":0, "carbs":0}
            if len(three_names) > 0:
                for name in three_names:
                    if find_similarity(recipe_name, name) >= 0:
                        three_names.append(recipe_name)
                        three_recipes.append(recipe)

                        list_ingredients = getIngredients(recipe)
                        for each in list_ingredients:
                            api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(each)
                            response = requests.get(api_url, headers={'X-Api-Key': apiNinja_api_key})

                            if response.status_code == 200:
                                response_data = json.loads(response.text)
                                # print("Response data:", response_data)
                                if len(response_data) == 0:
                                    # print("each:", each)
                                    continue
                                name = response_data[0]["name"]
                                nutrients["calories"] += response_data[0]["calories"]
                                nutrients["fat"] += response_data[0]["fat_total_g"]
                                nutrients["protein"] += response_data[0]["protein_g"]
                                nutrients["carbs"] += response_data[0]["carbohydrates_total_g"]

                            else:
                                print("Error:", response.status_code, response.text)

                        # print(nutrients)
                        three_nutrition.append(nutrients)


                        # Generate an image for the recipe name
                        image_response = openai.Image.create(
                            prompt="restaurant quality presentation, delicious photo of"+recipe_name + "on a plate",
                            n=1,
                            size="256x256",
                            response_format="b64_json",
                        )

                        #create json file for image
                        DATA_DIR = Path.cwd() / "responses"
                        DATA_DIR.mkdir(exist_ok=True)
                        JSON_FILE = DATA_DIR / f"{prompt[:5]}-{image_response['created']}.json"
                        with open(JSON_FILE, mode="w", encoding="utf-8") as file:
                            json.dump(image_response, file)

                        #convert json image data file to png
                        IMAGE_DIR = Path.cwd() / "public/generated_images"
                        IMAGE_DIR.mkdir(parents=True, exist_ok=True)

                        with open(JSON_FILE, mode="r", encoding="utf-8") as file:
                            image_response = json.load(file)

                        for index, image_dict in enumerate(image_response["data"]):
                            image_data = b64decode(image_dict["b64_json"])
                            image_file = IMAGE_DIR / f"{JSON_FILE.stem}-{index}.png"
                            with open(image_file, mode="wb") as png:
                                png.write(image_data)

                        full_path_to_image = image_file.as_posix()
                        image_url = full_path_to_image[full_path_to_image.find('generated_images'):]


                        three_images.append(image_url)
                        break
            else:
                three_names.append(recipe_name)
                three_recipes.append(recipe)


                list_ingredients = getIngredients(recipe)
                for each in list_ingredients:
                    api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(each)
                    response = requests.get(api_url, headers={'X-Api-Key': apiNinja_api_key})

                    if response.status_code == 200:
                        response_data = json.loads(response.text)
                        # print("Response data:", response_data)
                        if len(response_data) == 0:
                            # print("each:", each)
                            continue
                        name = response_data[0]["name"]
                        nutrients["calories"] += response_data[0]["calories"]
                        nutrients["fat"] += response_data[0]["fat_total_g"]
                        nutrients["protein"] += response_data[0]["protein_g"]
                        nutrients["carbs"] += response_data[0]["carbohydrates_total_g"]

                    else:
                        print("Error:", response.status_code, response.text)

                # print(nutrients)
                three_nutrition.append(nutrients)
                # Generate an image for the recipe name
                image_response = openai.Image.create(
                    prompt=recipe_name,
                    n=1,
                    size="256x256",
                    response_format="b64_json",
                )

                #create json file for image
                DATA_DIR = Path.cwd() / "responses"
                DATA_DIR.mkdir(exist_ok=True)
                JSON_FILE = DATA_DIR / f"{prompt[:5]}-{image_response['created']}.json"
                with open(JSON_FILE, mode="w", encoding="utf-8") as file:
                    json.dump(image_response, file)

                #convert json image data file to png
                IMAGE_DIR = Path.cwd() / "public/generated_images"
                IMAGE_DIR.mkdir(parents=True, exist_ok=True)

                with open(JSON_FILE, mode="r", encoding="utf-8") as file:
                    image_response = json.load(file)

                for index, image_dict in enumerate(image_response["data"]):
                    image_data = b64decode(image_dict["b64_json"])
                    image_file = IMAGE_DIR / f"{JSON_FILE.stem}-{index}.png"
                    with open(image_file, mode="wb") as png:
                        png.write(image_data)

                full_path_to_image = image_file.as_posix()
                image_url = full_path_to_image[full_path_to_image.find('generated_images'):]

                # print("first image url:", image_url)


                three_images.append(image_url)
            print(nutrients)
    # Create a list of recipe data
    recipe_data = []
    for recipe_name, recipe_text, image_url, nutrient_info in zip(three_names, three_recipes, three_images, three_nutrition):
        recipe_data.append({
            "recipe_name": recipe_name,
            "recipe_text": recipe_text,
            "image_url": image_url,
            "nutrient_info": nutrient_info,
            # "portions": portions,
        })

    session['portions'] = portions
    print(recipe_data)
    # Return the list of generated recipes and associated images as JSON
    return jsonify(recipe_data)



def find_similarity(string1, string2):
    # Tokenize the strings and create sets of unique words
    words1 = set(string1.split())
    words2 = set(string2.split())

    # Find the intersection of the two sets to get similar words
    similar_words = words1.intersection(words2)

    # Count the number of similar words
    count = len(similar_words)
    min_len = min(len(words1), len(words2))
    # print(words1, words2)
    # print(min_len - count)
    return min_len - count

def getIngredients(recipe):
    list_ingredients = []
    ingredients = recipe.split("Instructions")[0].split("Ingredients:")[1:][0].strip().split("\n")
    # Define a regex pattern to match any number
    pattern = r'^[•\-\s]*(\d+)'

    for i, item in enumerate(ingredients):
        match = re.search(pattern, item)
        if not match:
            continue
        digit = match.group(1)
        rest_of_string = item[match.end():].strip()
        temp = rest_of_string.split(' ')
        if temp[0][-1].isdigit():
            rest_of_string = ""
            for word in temp[1:]:
                rest_of_string += word + ' '
            digit = digit + temp[0]

        list_ingredients.append(digit + ' ' + rest_of_string)
    print(list_ingredients)
    return list_ingredients


def insert_nutrition_data(username, calories, protein, fat, carbs):
    nutrition_data = {
        # "username": username,
        "calories": calories,
        "protein": protein,
        "fat": fat,
        "carbs": carbs
    }
    db["nutrition_data"].insert_one(nutrition_data)


@application.route('/recipe_page', methods=['GET', 'POST'])
@cross_origin()
def recipe_page():
    calories = request.args.get('calories')
    protein = request.args.get('protein')
    fat = request.args.get('fat')
    carbs = request.args.get('carbs')
    print("calories", calories)
    # print("server: recipe text:", recipe_text)
    # portions = float(request.args.get('portions'))

    # print("here: portions", portions)

    if request.method == 'POST':
        if request.form.get('cookCheckbox') == 'on':
            print("ere")
            calories = float(request.form.get('calories'))
            protein = float(request.form.get('protein'))
            fat = float(request.form.get('fat'))
            carbs = float(request.form.get('carbs'))
            insert_nutrition_data(calories, protein, fat, carbs)
            response = jsonify({"message": "Success"})
            return response
    
        return render_template("index.html")
    return render_template("recipe_page.html", calories=calories, fat=fat, carbs=carbs, protein=protein)

@application.route('/view_nutrition_info', methods=['GET'])
def view_nutrition_info():
    total_calories, total_protein, total_carbs, total_fat = 0,0,0,0
    if "nutrition_data" in db.list_collection_names():
        username = session.get('username')
        nutrition_data = db["nutrition_data"].find({"username": username})
        for record in nutrition_data:
            total_fat += float(record["fat"])
            total_carbs += float(record["carbs"])
            total_protein += float(record["protein"])
            total_calories += float(record["calories"])
        print("sum data:", total_calories, total_protein, total_carbs, total_fat)
    return render_template("nutrition_info.html", total_calories=int(total_calories), total_carbs=int(total_carbs), total_fat=int(total_fat), total_protein=int(total_protein), username = session['username'])


if __name__ == '__main__':
    application.run(debug=True, port=3000)
    # app.run(debug=False, port=8080)
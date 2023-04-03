# survey-back-api

This API is the backbone of the Survey tool. It collects user feedbacks from the front modal and stores them in a SQLite database.
You can configure the rules for displaying the modal to your users from the YAML config file.
The API also provides an endpoint to fetch the feedbacks from a third party app, such as our BugPrediction.

## Requirements
- Python >= 3.8  
OR  
- Docker

## Endpoints

### POST /comments
Creates a new comment and stores it in the database.
It is intended to be used only by the Survey front library.

Request Body
A JSON object containing the comment details, including the feature URL, comment text, and the star rating.

Cookies
- user_id: The ID of the user who posted the comment.
- timestamp: The timestamp of when the modal was shown (in this case, it's used as the comment's time).
    
Response
- status code: 201 - Created
- response model: Comment - The newly created comment object.

### GET /comments
Retrieves all comments from the database.

Response
response model: List[Comment] - A list of comment objects.

## Usage

### Local installation

You need to run this command to install all the dependencies :

    pip install -r requirements.txt

You need to create a file in the project directory called ```.env```, you should copy the ```.env.example``` file.
You can change the values as needed. You should at least add the URL of your frontend app in ```CORS_ALLOW_ORIGINS```.
If you want a third party app to fetch the feedbacks, you should also add its URL to the origins, URLs separated with commas.

You can then run the API :

    python main.py

### Docker

First, ou need to create a file in the project directory called ```.env```, you should copy the ```.env.example``` file.
You can change the values as needed. You should at least add the URL of your frontend app in ```CORS_ALLOW_ORIGINS```.
If you want a third party app to fetch the feedbacks, you should also add its URL to the origins, URLs separated with commas.

Then build the Docker image using this command in the project folder :

    docker build -t survey-back-api .

Finally, create a container and run it from the image :

    docker run -dp 8000:8000 survey-back-api

## Test 

You can run the unit tests : 

    python -m unittest discover tests

The tests can also be run within a Docker container. After building the image, run this command :

    docker run --rm [image-name] python -m unittest discover tests

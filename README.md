# survey-back-api

This API is the backbone of the Survey tool. It collects user feedbacks from the front modal and stores them in a SQLite database.
You can configure the rules for displaying the modal to your users from the YAML config file.
The API also provides an endpoint to fetch the feedbacks from a third party app, such as our BugPrediction.

## Endpoints

POST /comments
Creates a new comment and stores it in the database.

Request Body
- commentcookie: A JSON object containing the comment details, including the feature URL, comment text, and th rating.
- cookie : user_id, The ID of the user who posted the comment.
- cookie : timestamp, The timestamp of when the comment was posted.
    
Response
status code: 201 - Created
response model: Comment - The newly created comment object.
GET /comments
Retrieves all comments from the database.

Response
response model: List[Comment] - A list of comment objects.

## Functionality
This API uses FastAPI and Pydantic for type validation and dependency injection. The SQLite database is managed using the databases library. The API has the following functionalities:

Creating a Comment
You can create a new comment using the POST /comments endpoint. The endpoint accepts a JSON object containing the comment details, including the feature URL, comment text, and other metadata. The user ID and timestamp are optional. The comment is stored in the database, and the API returns the newly created comment object.

Reading Comments
You can retrieve all comments from the database using the GET /comments endpoint. The API returns a list of comment objects.

Comment Validation
The API validates that the rating in a comment is an integer between 1 and 5. If the rating is invalid, the API returns an error message.

Project Creation
The API automatically creates a new project in the database when a comment is added for a new project. This ensures that there are no orphaned comments in the database.
## Usage

You need to run this commnand to install all the dependencies :

    pip install -r requirements.txt

You need to create a file in the project directory called ```.env```, you should copy the ```.env.example``` file.
You can change the values as needed. You should at least add the URL of your frontend app in ```CORS_ALLOW_ORIGINS```.
If you want a third party app to fetch the feedbacks, you should also add its URL to the origins, URLs separated with commas.

You can then run the API :

    python main.py

## Test 

You can run the unittests : 

    python -m unittest discover test

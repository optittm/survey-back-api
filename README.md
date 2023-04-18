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

### GET /rules

Retrieves the rules for displaying the feedback modal based on the provided feature URL.

Request Query Parameters
featureUrl: The URL of the feature for which to retrieve the rules.
Cookies
- user_id: The ID of the user who posted the comment.
- timestamp: The timestamp of when the modal was last shown.

Response
- status code: 200 - OK
- response model: bool - True if the modal should be displayed based on the retrieved rules, False otherwise.

Example usage: GET ```/rules?featureUrl=https://www.example.com/feature1```  
Example response: true
## Usage

### Local installation

1. Clone the repository.
2. Install dependencies by running ```pip install -r requirements.txt```.
3. Create a file in the project directory called ```.env```, and copy the ```.env.example``` file to it.
4. Update the values in .env as needed. You should at least add the URL of your frontend app in ```CORS_ALLOW_ORIGINS```.
5. If you want a third-party app to fetch feedback, add its URL to the ```CORS_ALLOW_ORIGINS``` field, separated by commas.
6. Fill in the rules.yaml file with the rules for displaying the feedback modal for your projects.
7. Run the API by running ```python main.py```.

### Docker

1. Clone the repository.
2. Create a file in the project directory called ```.env```, and copy the ```.env.example``` file to it.
3. Update the values in ```.env``` as needed. You should at least add the URL of your frontend app in ```CORS_ALLOW_ORIGINS```.
4. If you want a third-party app to fetch feedback, add its URL to the ```CORS_ALLOW_ORIGINS``` field, separated by commas.
5. Fill in the rules.yaml file with the rules for displaying the feedback modal for your projects.
6. Build the Docker image by running ```docker build -t survey-back-api .``` in the project folder.
7. Create and run a container from the image by running ```docker run -dp 8000:8000 survey-back-api```.

## Test 

To run the unit tests:

1. Install dependencies by running ```pip install -r requirements.txt```.
2. Run the tests by running ```python -m unittest discover tests```.

You can also run the tests within a Docker container:

1. Build the Docker image as described in the Docker section above.
2. Run the tests by running ```docker run --rm [image-name] python -m unittest discover tests```.
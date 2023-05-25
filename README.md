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
A JSON object containing the comment details, including the feature URL, comment text, star rating, and the user fingerprint generated by the [front library](https://github.com/optittm/survey-front-library)

Cookies

- user_id: The ID of the user who posted the comment.
- timestamp: The timestamp of when the modal was shown (in this case, it's used as the comment's time).

Response

- status code: 201 - Created
- response model: Comment - The newly created comment object.

**WARNING**  
You can choose whether to use the Fingerprint or the cookie user ID by changing the value of `USE_FINGERPRINT` in the `.env` file. You should consider disabling the fingerprint if your data storage and treatment doesn't comply with GPDR.  
You can find more information about how the fingerprint is generated at https://github.com/fingerprintjs/fingerprintjs

### GET /comments

Retrieves comments from the database. It supports filtering by various parameters.

Request Query Parameters

- project_name: The name of the project to filter by.
- feature_url: The URL of the feature to filter by.
- user_id: The ID of the user to filter by.
- timestamp_start: The minimum timestamp of the comments to filter by (in ISO 8601 format).
- timestamp_end: The maximum timestamp of the comments to filter by (in ISO 8601 format).
- content_search: A search query (regex) to filter comments by. It searches in the comment text field.
- rating_min: The minimum rating to filter by.
- rating_max: The maximum rating to filter by.
- page: The current page number (default: 1).
- page_size: The number of comments per page (default: 20).

Response  
response model: List[Comment] - A list of comment objects matching the specified filters. If no filters are provided, it returns all comments.

Example usage: GET /comments?project_name=my-project&feature_url=/feature1&user_id=user123&timestamp_start=2022-01-01T00:00:00Z&timestamp_end=2022-12-31T23:59:59Z&content_search=bug&ratin_min=3&rating_max=5&page=1&page_size=20

## Pagination

The `/comments` endpoint supports pagination for retrieving large data sets. The following query parameters can be used to control pagination:

- page: The current page number (default: 1).
- page_size: The number of comments per page (default: 20).

The API response includes pagination information such as the total number of comments, the current page, page size, and links to the next and previous pages.

### GET /rules

Retrieves the rules for displaying the feedback modal based on the provided feature URL.

Request Query Parameters

- featureUrl: The URL of the feature for which to retrieve the rules.

Cookies

- user_id: The ID of the user who posted the comment.
- timestamp: The timestamp of when the modal was last shown.

Response

- status code: 200 - OK
- response model: bool - True if the modal should be displayed based on the retrieved rules, False otherwise.

Example usage: GET `/rules?featureUrl=https://www.example.com/feature1`  
Example response: true

### GET /survey-report

Generates an HTML report for the survey.

Response

- status code: 200 - OK
- response model: str - The generated HTML report.

### GET /survey-report/project

Generates a HTML report for a specific project survey.

Request Query Parameters

- timestamp_start: The minimum timestamp of the trends to filter by (in ISO 8601 format).
- timestamp_end: The maximum timestamp of the trends to filter by (in ISO 8601 format).

Response

- status code: 200 - OK
- response model: str - The generated HTML report.

Example usage: GET `/survey-report/project/23?timestamp_start=01-01-2020&timestamp_end=01-01-2022`

## Usage

### Local installation

1. Clone the repository.
2. Install dependencies by running `pip install -r requirements.txt`.
3. Create a file in the project directory called `.env`, and copy the `.env.example` file to it.
4. Update the values in .env as needed. You should at least add the URL of your frontend app in `CORS_ALLOW_ORIGINS`.
5. If you want a third-party app to fetch feedback, add its URL to the `CORS_ALLOW_ORIGINS` field, separated by commas.
6. Fill in the rules.yaml file with the rules for displaying the feedback modal for your projects.
7. Run the API by running `python main.py`.

### Docker

1. Clone the repository.
2. Create a file in the project directory called `.env`, and copy the `.env.example` file to it.
3. Update the values in `.env` as needed. You should at least add the URL of your frontend app in `CORS_ALLOW_ORIGINS`.
4. If you want a third-party app to fetch feedback, add its URL to the `CORS_ALLOW_ORIGINS` field, separated by commas.
5. Fill in the rules.yaml file with the rules for displaying the feedback modal for your projects.
6. Build the Docker image by running `docker build -t survey-back-api .` in the project folder.
7. Create and run a container from the image by running `docker run -dp 8000:8000 survey-back-api`.

## Tests

To run the unit tests:

1. Install dependencies by running `pip install -r requirements.txt`.
2. Run the tests by running `python -m unittest discover tests`.

You can also run the tests within a Docker container:

1. Build the Docker image as described in the Docker section above.
2. Run the tests by running `docker run --rm [image-name] python -m unittest discover tests`.

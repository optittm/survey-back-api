# Survey Back API

Welcome to the Survey project!

Survey is a feedback collection tool that allows users to provide comments, ratings, and feedback on various features of your application. It consists of multiple components, including the front-end library, the back-end API, and the reporting module.

## Repositories

Here are the repositories related to the Survey project:

- [Survey Front Library](https://github.com/optittm/survey-front-library): The front-end library for the Survey project.
- Survey Back API: The back-end API for the Survey project. You are currently in this repository.
- [Survey Front Modal](https://github.com/optittm/survey-front-modal): The reporting module for the Survey project. A popup modal asking the user for feedback.

## Requirements

- Python >= 3.8
  OR
- Docker

## Documentation

Please refer to the following documentation for detailed information about the Survey back-end API:

- [Comments API](docs/api/comments.md)
- [Rules API](docs/api/rules.md)
- [Survey Reporting API](docs/api/report.md)
- [Projects API](docs/api/projects.md)
- [Sentiment Analysis](docs/nlp.md)
- [Security](docs/security.md)
- [Database structure](docs/database_structure.md)

## Usage

### Local Installation

To run the Survey back-end API locally, follow these steps:

1. Clone the repository.
2. Install dependencies by running `pip install -r requirements.txt`.
3. Create a file in the project directory called `.env` and copy the `.env.example` file to it.
4. Update the values in `.env` as needed. Make sure to add the URL of your frontend app to `CORS_ALLOW_ORIGINS`.
5. If you want a third-party app to fetch feedback, add its URL to the `CORS_ALLOW_ORIGINS` field, separated by commas.
6. Fill in the `rules.yaml` file with the rules for displaying the feedback modal for your projects.
7. Run the API by executing `python main.py`.

### Docker

To run the Survey back-end API using Docker, follow these steps:

1. Clone the repository.
2. Create a file in the project directory called `.env` and copy the `.env.example` file to it.
3. Update the values in `.env` as needed. Make sure to add the URL of your frontend app to `CORS_ALLOW_ORIGINS`.
4. If you want a third-party app to fetch feedback, add its URL to the `CORS_ALLOW_ORIGINS` field, separated by commas.
5. Fill in the `rules.yaml` file with the rules for displaying the feedback modal for your projects.
6. Build the Docker image by running `docker build -t survey-back-api .` in the project folder.
7. Create and run a container from the image by running `docker run -dp 8000:8000 survey-back-api`.

## Tests

To run the unit tests for the Survey back-end API, follow these steps:

1. Install dependencies by running `pip install -r requirements.txt`.
2. Run the tests by executing `python -m unittest discover tests`.

You can also run the tests within a Docker container:

1. Build the Docker image as described in the Docker section above.
2. Run the tests by executing `docker run --rm [image-name] python -m unittest discover tests`.

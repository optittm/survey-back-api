# survey-back-api

This API is the backbone of the Survey tool. It collects user feedbacks from the front modal and stores them in a SQLite database.
You can configure the rules for displaying the modal to your users from the YAML config file.
The API also provides an endpoint to fetch the feedbacks from a third party app, such as our BugPrediction.

## Endpoints

These can also be seen on the generated documentation when running the API at /docs.

TODO

## Usage

You need to run this commnand to install all the dependencies :

    pip install -r requirements.txt

You need to create a file in the project directory called ```.env```, you should copy the ```.env.example``` file.
You can change the values as needed. You should at least add the URL of your frontend app in ```CORS_ALLOW_ORIGINS```.
If you want a third party app to fetch the feedbacks, you should also add its URL to the origins, URLs separated with commas.

You can then run the API :

    python main.py

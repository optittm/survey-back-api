# Projects API

The Projects API is a web application that provides endpoints to retrieve information about projects, including project details, feature ratings, rules, and average ratings.

## Usage

### Get Projects

- **Endpoint:** `/projects`
- **Method:** GET
- **Description:** Retrieve a list of projects with their respective IDs and names.
- **Response:** Returns a list of dictionaries containing the ID and name of each project.

### Get Project Feature Rating

- **Endpoint:** `/project/{id}/avg_feature_rating`
- **Method:** GET
- **Description:** Returns the feature ratings for a given project ID.
- **Path Parameters:**
  - `id` (integer): The ID of the project to retrieve feature ratings for.
- **Response:** Returns a list of dictionaries containing the feature URL and rating for the specified project. If the project is not found, returns a dictionary with the error message.

### Get Project Rules

- **Endpoint:** `/projects/{id}/rules`
- **Method:** GET
- **Description:** Returns the rules for a project with the given ID.
- **Path Parameters:**
  - `id` (integer): The ID of the project to retrieve rules for.
- **Response:** Returns a list of rules for the project, or an error dictionary if the project is not found.

### Get Project Rating

- **Endpoint:** `/project/{id}/avg_rating`
- **Method:** GET
- **Description:** Retrieve the average rating of a project with the given ID.
- **Path Parameters:**
  - `id` (integer): The ID of the project to retrieve the rating for.
- **Response:** Returns a dictionary containing the project ID and its average rating, or an error message if the project was not found or if its name is not included in the list of project names in the YamlRulesRepository.

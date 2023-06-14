# Comment API

The Comment API is a web application that allows users to create and retrieve comments for various features. It provides endpoints to create comments, perform sentiment analysis, and retrieve comments based on various filters.

## Usage

### Create Comment

- **Endpoint:** `/comments`
- **Method:** POST
- **Description:** Creates a new comment.
- **Request Body:** Expects a JSON object with the following fields:
  - `feature_url` (string): The URL of the feature associated with the comment.
  - `rating` (integer): The rating given to the feature.
  - `comment` (string): The comment text.
- **Cookies:** Requires the following cookies to be set:
  - `user_id`: The ID of the user creating the comment.
  - `timestamp`: The timestamp when the comment is created.
- **Response:** Returns the created comment object.
**WARNING**  
You can choose whether to use the Fingerprint or the cookie user ID by changing the value of `USE_FINGERPRINT` in the `.env` file. You should consider disabling the fingerprint if your data storage and treatment doesn't comply with GPDR.  
You can find more information about how the fingerprint is generated at https://github.com/fingerprintjs/fingerprintjs  

### Get Comments

- **Endpoint:** `/comments`
- **Method:** GET
- **Description:** Retrieves comments based on specified filters.
- **Query Parameters:** Supports the following optional query parameters to filter the comments:
  - `project_name` (string): Filters comments by project name.
  - `feature_url` (string): Filters comments by feature URL.
  - `user_id` (string): Filters comments by user ID.
  - `timestamp_start` (string): Filters comments with a timestamp greater than or equal to the specified start timestamp. (in ISO 8601 format)
  - `timestamp_end` (string): Filters comments with a timestamp less than or equal to the specified end timestamp. (in ISO 8601 format)
  - `content_search` (string): Filters comments by a search query (regex). It searches in the comment text field.
  - `rating_min` (integer): Filters comments with a rating greater than or equal to the specified minimum rating.
  - `rating_max` (integer): Filters comments with a rating less than or equal to the specified maximum rating.
  - `page` (integer): Specifies the page number for pagination. Default is 1.
  - `page_size` (integer): Specifies the number of comments per page. Default is 20.
- **Response:** Returns a dictionary containing the filtered comments, pagination information, and total comment count.
-**Example usage:** GET /comments?project_name=my-project&feature_url=/feature1&user_id=user123&timestamp_start=2022-01-01T00:00:00Z&timestamp_end=2022-12-31T23:59:59Z&content_search=bug&ratin_min=3&rating_max=5&page=1&page_size=20

### Pagination

The `/comments` endpoint supports pagination for retrieving large data sets. The following query parameters can be used to control pagination:

- page: The current page number (default: 1).
- page_size: The number of comments per page (default: 20).

The API response includes pagination information such as the total number of comments, the current page, page size, and links to the next and previous pages.

## Regex for featureUrl  
The featureUrl parameter supports matching based on regular expressions. The regular expression pattern used is as follows:  

The provided featureUrl is matched against the feature_url values in the rule configuration.

The pattern should match the complete feature_url value in the rule configuration.
Special characters within the feature_url should be properly escaped to ensure correct matching.
By default, the pattern is wrapped in word boundaries (\b) to match the entire URL and avoid partial matches. 
**Warning:** The returned rule will be the first rule that matches in the yaml file. So if you want a default rule, you should put it at the end of the list. 


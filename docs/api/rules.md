# Rules API

The Rules API is a web application that provides an endpoint to display a modal based on predefined rules for a given feature URL.

## Usage

### Show Modal

- **Endpoint:** `/rules`
- **Method:** GET
- **Description:** Determines whether to show a modal for a specific feature URL based on predefined rules.
- **Query Parameters:**
  - `featureUrl` (string): The URL of the feature for which to display the modal.
- **Cookies:**
  - `user_id` (string, optional): The user ID cookie. If not provided, a new user ID will be generated and set as the cookie.
  - `timestamp` (string, optional): The timestamp cookie. If provided, it should be encrypted.
- **Response:** Returns a boolean value indicating whether to display the modal for the specified feature URL.
- **Example usage:** GET ```/rules?featureUrl=https://www.example.com/feature1```  
Example response: true 

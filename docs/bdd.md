# Database Structure - Survey Back API

The database (DB) of the Survey Back API is designed to store user comments, feedback form presentation rules, and survey report-related data.

## Database Tables

The DB includes the following tables:

1. **Table `Comment`**: This table stores user comments.

   - Columns:
     - `id` (primary key): Unique identifier for the comment.
     - `project_id` : ID of the project associated with the comment.
     - `user_id`: Identifier of the user who posted the comment.
     - `timestamp`: Timestamp of the comment.
     - `feature_url`: URL of the feature associated with the comment.
     - `rating`: Rating given by the user.
     - `comment`: Text of the comment.

2. **Table `Display`**: 

   - Columns:
     - `id` (primary key): Unique identifier for the display.
     - `project_id` : ID of the project.
     - `user_id`: Identifier of the user.
     - `timestamp`: Timestamp of the comment.
     - `feature_url`: URL of the feature.

3. **Table `Project`**: This table stores information about survey projects.

   - Columns:
     - `id` (primary key): Unique identifier for the project.
     - `project_name`: Name of the project.

4. **Table `ProjectEncryption`**: This table stores project encryption information.

   - Columns:
     - `id` (primary key): Unique identifier for the response.
     - `project_id`: Foreign key referencing the `Project` table's `id`.
     - `encryption_key`: Encryption key associated with the project.

## Relationships between Tables

The Survey Back API database includes the following relationships between tables:

1. Relationship between `Comment` and `Project` tables:
   - Each comment in the `Comment` table is associated with a project from the `Project` table.
   - The `project_id` column in the `Comment` table is a foreign key referencing the `id` column in the `Project` table.

2. Relationship between `Display` and `Project` tables:
   - Each display in the `Display` table is associated with a project from the `Project` table.
   - The `project_id` column in the `Display` table is a foreign key referencing the `id` column in the `Project` table.

3. Relationship between `ProjectEncryption` and `Project` tables:
   - Each project encryption record in the `ProjectEncryption` table is associated with a project from the `Project` table.
   - The `project_id` column in the `ProjectEncryption` table is a foreign key referencing the `id` column in the `Project` table.

These relationships ensure data integrity and enable efficient querying and retrieval of information across the related tables.


## Database Schema

Here is a visual schema representing the structure of the database:

                                    +-----------------------+
                                    |        Comment        |
                                    +-----------------------+
                                    | id (primary key)      |
                                    | project_id (FK)       |
                                    | user_id               |
                                    | timestamp             |
                                    | feature_url           |
                                    | rating                |
                                    | comment               |
                                    +-----------------------+

                                    +-----------------------+
                                    |        Display        |
                                    +-----------------------+
                                    | id (primary key)      |
                                    | project_id (FK)       |
                                    | user_id               |
                                    | timestamp             |
                                    | feature_url           |
                                    +-----------------------+

                                    +-----------------------+
                                    |        Project        |
                                    +-----------------------+
                                    | id (primary key)      |
                                    | project_name          |
                                    +-----------------------+

                                    +-----------------------+
                                    |   ProjectEncryption   |
                                    +-----------------------+
                                    | id (primary key)      |
                                    | project_id (FK)       |
                                    | encryption_key        |
                                    +-----------------------+
                                    
This represents the tables `Comment`, `Display`, `Project`, and `ProjectEncryption` with their respective columns. Each column represents a specific attribute of the data stored in the database.
# Database Structure - Survey Back API

The database (DB) of the Survey Back API is designed to store user comments, feedback form presentation rules, and survey report-related data.

## Database Schema
```plaintext
Table: Comment
+----------------+-------------------+---------------------------------------+
| Column         | Type              | Description                           |
+----------------+-------------------+---------------------------------------+
| id             | Integer (PK)      | Unique identifier for the comment      |
| project_id     | Integer (FK)      | ID of the associated project           |
| user_id        | Integer           | Identifier of the user who posted      |
| timestamp      | DateTime          | Timestamp of the comment               |
| feature_url    | String            | URL of the associated feature          |
| rating         | Integer           | Rating given by the user               |
| comment        | Text              | Text of the comment                    |
+----------------+-------------------+---------------------------------------+

Table: Display
+----------------+-------------------+---------------------------------------+
| Column         | Type              | Description                           |
+----------------+-------------------+---------------------------------------+
| id             | Integer (PK)      | Unique identifier for the display      |
| project_id     | Integer (FK)      | ID of the associated project           |
| user_id        | Integer           | Identifier of the user                 |
| timestamp      | DateTime          | Timestamp of the display               |
| feature_url    | String            | URL of the associated feature          |
+----------------+-------------------+---------------------------------------+

Table: Project
+----------------+-------------------+---------------------------------------+
| Column         | Type              | Description                           |
+----------------+-------------------+---------------------------------------+
| id             | Integer (PK)      | Unique identifier for the project      |
| project_name   | String            | Name of the project                    |
+----------------+-------------------+---------------------------------------+

Table: ProjectEncryption
+----------------+-------------------+---------------------------------------+
| Column         | Type              | Description                           |
+----------------+-------------------+---------------------------------------+
| id             | Integer (PK)      | Unique identifier for the encryption   |
| project_id     | Integer (FK)      | ID of the associated project           |
| encryption_key | String            | Encryption key for the project         |
+----------------+-------------------+---------------------------------------+
```                               
This represents the tables `Comment`, `Display`, `Project`, and `ProjectEncryption` with their respective columns. Each column represents a specific attribute of the data stored in the database.

## Relationships between Tables  

Relationship between Comment and Project tables:

Each comment in the Comment table is associated with a project from the Project table.
The project_id column in the Comment table is a foreign key referencing the id column in the Project table.
Relationship between Display and Project tables:

Each display in the Display table is associated with a project from the Project table.
The project_id column in the Display table is a foreign key referencing the id column in the Project table.
Relationship between ProjectEncryption and Project tables:

Each project encryption record in the ProjectEncryption table is associated with a project from the Project table.
The project_id column in the ProjectEncryption table is a foreign key referencing the id column in the Project table.
These relationships maintain the integrity of the data and facilitate efficient querying and retrieval across the related tables.
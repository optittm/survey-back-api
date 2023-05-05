from datetime import datetime
from typing import List, Union
import logging
import sqlite3

from models.comment import Comment, CommentPostBody
from models.display import Display
from models.project import Project, ProjectEncryption
from utils.encryption import Encryption


class SQLiteRepository:

    def __init__(self, config):
        self.db_name = config["survey_db"].replace("sqlite:///", "")

        self.__create_view()

    def __create_view(self):
        """
        Creates views in the database to calculate statistics on project comments and displays.

        This method creates four views in the database:
            - 'feature_rating_avg': calculates the average rating for each feature of a project from comments.
            - 'project_rating_avg': calculates the average rating for each project from comments.
            - 'number_comment_by_project': calculates the number of comments for each project.
            - 'number_display_by_project': calculates the number of displays for each project.

        If a view already exists in the database, the method ignores its creation.
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        # All the creation of the view are ignored if the view already exist
        # Create the view that count the average rating of a feature of a project
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS feature_rating_avg AS
                SELECT project_id, feature_url, AVG(rating) AS average_rating
                FROM Comment
                GROUP BY project_id, feature_url;
        ''')
        # Create the view that count the average rating of a project
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS project_rating_avg AS
                SELECT project_id, AVG(rating) AS average_rating
                FROM Comment
                GROUP BY project_id;
        ''')
        # Create the view that count the number of comment by project
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS number_comment_by_project AS
                SELECT project_id, count(timestamp) AS number_comment
                FROM Comment
                GROUP BY project_id;
        ''')
        # Create the view that count the number of display by project
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS number_display_by_project AS
                SELECT project_id, count(timestamp) AS number_display
                FROM Display
                GROUP BY project_id;
        ''')
        conn.commit()
        cursor.close()
        conn.close()

    def get_project_avg_rating(self, project_id: int):
        """
        Retrieve the average rating of a project from the `project_rating_avg` view.

        Args:
            project (Project): The project object for which to retrieve the average rating.

        Returns:
            float: The average rating of the project.

        Raises:
            IndexError: If the result of the query is empty.
        """
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(f'''
            SELECT average_rating 
            FROM project_rating_avg
            WHERE project_id = {project_id};
        ''')
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result[0][0]

    def get_feature_avg_rating(self, project_id: int, feature_url: str):
        """
        Retrieves the average rating for a given feature of a specific project from 
        the database.

        This method executes an SQL query to retrieve the average rating associated 
        with the specified feature of a specific project. The average rating is extracted 
        from the 'feature_rating_avg' view created by the '__create_views' method.

        Args:
            project (Project): the Project object representing the project for which the 
                average rating should be retrieved.
            feature_url (str): the URL of the feature for which the average rating should 
                be retrieved.

        Returns:
            float: the average rating of the specified feature for the specified project. 
                If the average rating is not found, returns None.
        """
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(f'''
            SELECT average_rating
            FROM feature_rating_avg
            WHERE project_id = {project_id}
                AND feature_url = "{feature_url}";
        ''')
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result[0][0]

    def get_number_of_comment(self, project_id: int):
        """
        Retrieves the number of comments for a specific project from the database.

        This method executes an SQL query to retrieve the number of comments associated 
        with a specific project. The number of comments is extracted from the 
        'number_comment_by_project' view created by the '__create_views' method.

        Args:
            project (Project): the Project object representing the project for which the 
                number of comments should be retrieved.

        Returns:
            int: the number of comments for the specified project. If the number of comments 
                is not found, returns None.
        """
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(f'''
            SELECT number_comment
            FROM number_comment_by_project
            WHERE project_id = {project_id};
        ''')
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result[0][0]

    def get_number_of_display(self, project_id: int):
        """
        Retrieves the number of displays for a specific project from the database.

        This method executes an SQL query to retrieve the number of displays associated 
        with a specific project. The number of displays is extracted from the 
        'number_display_by_project' view created by the '__create_views' method.

        Args:
            self: the instance of the class.
            project (Project): the Project object representing the project for which the 
                number of displays should be retrieved.

        Returns:
            int: the number of displays for the specified project. If the number of displays 
                is not found, returns None.
        """

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(f'''
            SELECT number_display
            FROM number_display_by_project
            WHERE project_id = {project_id};
        ''')
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result[0][0]

    async def create_comment(
        self,
        comment_body: CommentPostBody,
        user_id: str,
        timestamp: str,
        project_name: str,
    ) -> Comment:
        """
        Creates a comment in the database

        Args:
            - comment_body: main part of the comment
            - user_id: the UUID of the user posting the comment
            - timestamp: timestamp of the comment in ISO 6801 format
            - project_name: the project name

        Returns:
            The saved Comment object
        """

        projects = await Project.filter(name=project_name)

        if len(projects) == 0:
            logging.warning("Project missing on comment creation")

            # ajouter une partie qui permet de gérer la clé
            project = await self.create_project(Project(name=project_name))
        else:
            project = projects[0]

        new_comment = Comment(
            project_id=project.id,
            feature_url=comment_body.feature_url,
            user_id=user_id,
            timestamp=timestamp,
            rating=comment_body.rating,
            comment=comment_body.comment,
        )
        id = await new_comment.insert()
        new_comment.id = id
        logging.debug(f"Comment created in DB: {new_comment}")
        return new_comment

    async def read_comments(self) -> List[Comment]:
        comments = await Comment.all()
        return comments

    async def create_project(self, project: Project):
        projects = await Project.filter(name=project.name)

        if len(projects) == 0:
            id = await project.insert()
            project.id = id
            logging.debug(f"Project created in DB: {project}")
            projet_encryption = ProjectEncryption(
                project_id=project.id, encryption_key=Encryption.generate_key()
            )
            await projet_encryption.insert()
            logging.debug(f"Project Encryption created in DB: {projet_encryption}")
        else:
            logging.debug("Cannot create project, already exists in DB")
            project = projects[0]

        return project

    async def get_project_by_id(self, project_id: int) -> Project:
        project = await Project.get(id=project_id)
        return project

    async def get_project_by_name(self, project_name: str) -> Union[Project, None]:
        projects = await Project.filter(name=project_name)
        if len(projects):
            return projects[0]
        else:
            return None

    async def get_encryption_by_project_id(
        self, project_id: int
    ) -> Union[ProjectEncryption, None]:
        encryptions = await ProjectEncryption.filter(project_id=project_id)
        if len(encryptions):
            return encryptions[0]
        else:
            return None
        
    async def create_display(
            self, project_name: str, user_id: int, timestamp: str, feature_url: str
    ) -> Union[Display, None]:
        
        projects = await Project.filter(name=project_name)

        if len(projects) == 0:
            logging.warning("Project missing on display creation")

            # ajouter une partie qui permet de gérer la clé
            project = await self.create_project(Project(name=project_name))
        else:
            project = projects[0]

        new_display = Display(
            project_id = project.id,
            user_id = user_id,
            timestamp = timestamp,
            feature_url = feature_url
        )

        id = await new_display.insert()
        new_display.id = id
        logging.debug(f"Display created in DB: {new_display}")
        return new_display
        
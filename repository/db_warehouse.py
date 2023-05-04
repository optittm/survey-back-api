
import sqlite3

from models.project import Project


class DBWarehouse:
    """
    This class represents a database warehouse that get data related to 
    project ratings and comments. It allows to retrieve statistics
    about the projects and their features stored in the database.

    Attributes:
    - db_name (str): the name of the database
    - conn (sqlite3.Connection): the connection to the database
    """
    
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)

        self.__create_views()

    def __create_views(self):
        """
        Creates views in the database to calculate statistics on project comments and displays.

        This method creates four views in the database:
            - 'feature_rating_avg': calculates the average rating for each feature of a project from comments.
            - 'project_rating_avg': calculates the average rating for each project from comments.
            - 'number_comment_by_project': calculates the number of comments for each project.
            - 'number_display_by_project': calculates the number of displays for each project.

        If a view already exists in the database, the method ignores its creation.
        """
        cursor = self.conn.cursor()
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
                GROUP BY project_id
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
        self.conn.commit()
        cursor.close()

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

        cursor = self.conn.cursor()
        cursor.execute(f'''
            SELECT average_rating 
            FROM project_rating_avg
            WHERE project_id = {project_id};
        ''')
        result = cursor.fetchall()
        cursor.close()
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
        
        cursor = self.conn.cursor()
        cursor.execute(f'''
            SELECT average_rating
            FROM feature_rating_avg
            WHERE project_id = {project_id}
                AND feature_url = "{feature_url}";
        ''')
        result = cursor.fetchall()
        cursor.close()
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

        cursor = self.conn.cursor()
        cursor.execute(f'''
            SELECT number_comment
            FROM number_comment_by_project
            WHERE project_id = {project_id};
        ''')
        result = cursor.fetchall()
        cursor.close()
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

        cursor = self.conn.cursor()
        cursor.execute(f'''
            SELECT number_display
            FROM number_display_by_project
            WHERE project_id = {project_id};
        ''')
        result = cursor.fetchall()
        cursor.close()
        return result[0][0]


    def close(self):
        self.conn.close()
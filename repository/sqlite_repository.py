from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import logging
import sqlite3
from sqlalchemy.orm import Session

from models.comment import Comment, SentimentEnum
from models.display import Display
from models.project import Project, ProjectEncryption
from models.views import FeatureRatingAvg, NumberCommentByProject, NumberDisplayByProject, ProjectRatingAvg
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
        cursor.execute(
            """
            CREATE VIEW IF NOT EXISTS feature_rating_avg AS
                SELECT project_id, feature_url, AVG(rating) AS average_rating
                FROM Comment
                GROUP BY project_id, feature_url;
        """
        )
        # Create the view that count the average rating of a project
        cursor.execute(
            """
            CREATE VIEW IF NOT EXISTS project_rating_avg AS
                SELECT project_id, AVG(rating) AS average_rating
                FROM Comment
                GROUP BY project_id;
        """
        )
        # Create the view that count the number of comment by project
        cursor.execute(
            """
            CREATE VIEW IF NOT EXISTS number_comment_by_project AS
                SELECT project_id, count(timestamp) AS number_comment
                FROM Comment
                GROUP BY project_id;
        """
        )
        # Create the view that count the number of display by project
        cursor.execute(
            """
            CREATE VIEW IF NOT EXISTS number_display_by_project AS
                SELECT project_id, count(timestamp) AS number_display
                FROM Display
                GROUP BY project_id;
        """
        )
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

        with Session(Comment.__metadata__.database.engine) as session:
            query = session.query(ProjectRatingAvg.average_rating) \
               .filter(ProjectRatingAvg.project_id == project_id)

            result = query.all()
            try:
                return result[0][0]
            except IndexError:
                return 0


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

        with Session(Comment.__metadata__.database.engine) as session:
            query = session.query(FeatureRatingAvg.average_rating) \
               .filter(FeatureRatingAvg.project_id == project_id, 
                       FeatureRatingAvg.feature_url == feature_url)

            result = query.all()
            try:
                return result[0][0]
            except IndexError:
                return 0

    async def get_features_urls_by_project_name(self, project_name: str):
        """
        Retrieves all features_urls for a specific project name from the database.

        Args:
            project_name (str): the Project name representing the project for which the
                feature_urls should be retrieved.

        Returns:
            feature_urls ([str]): the list of feature_urls for the specified project.
        """
        project = await self.get_project_by_name(project_name)

        if project is None:
            return []

        with Session(Comment.__metadata__.database.engine) as session:
            query = session.query(FeatureRatingAvg.feature_url).filter(
                FeatureRatingAvg.project_id == project.id
            ).all()

        return [row[0] for row in query]

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

        with Session(Comment.__metadata__.database.engine) as session:
            query = session.query(NumberCommentByProject.number_comment) \
               .filter(NumberCommentByProject.project_id == project_id)

            result = query.all()
            try:
                return result[0][0]
            except IndexError:
                return 0

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

        with Session(Comment.__metadata__.database.engine) as session:
            query = session.query(NumberDisplayByProject.number_display) \
               .filter(NumberDisplayByProject.project_id == project_id)

            result = query.all()
            try:
                return result[0][0]
            except IndexError:
                return 0

    async def create_comment(
        self,
        feature_url: str,
        rating: int,
        comment: str,
        user_id: str,
        timestamp: str,
        project_name: str,
        language: str,
        sentiment: SentimentEnum = None,
        sentiment_score: float = None,
    ) -> Comment:
        """
        Creates a comment in the database

        Args:
            - feature_url: URL of the feature the comment is for
            - rating: the ratong of the comment, from 1 to 5 stars
            - comment: the text of the comment
            - user_id: the UUID of the user posting the comment
            - timestamp: timestamp of the comment in ISO 6801 format
            - project_name: the project name
            - language: two-character ISO639-1 code
            - sentiment: whether the comment is positive or negative, given by sentiment analysis. None when comment has no text
            - sentiment_score: the score of confidence for the sentiment, given by sentiment analysis. None when comment has no text

        Returns:
            The saved Comment object
        """

        # Get project by name
        projects = await Project.filter(name=project_name)

        if len(projects) == 0:
            # If project does not exist, create new project
            logging.warning("Project missing on comment creation")
            project = await self.create_project(Project(name=project_name))
        else:
            project = projects[0]
        # Create new comment object and insert into database
        new_comment = Comment(
            project_id=project.id,
            feature_url=feature_url,
            user_id=user_id,
            timestamp=timestamp,
            rating=rating,
            comment=comment,
            language=language,
            sentiment=sentiment.value if sentiment is not None else sentiment,
            sentiment_score=sentiment_score,
        )
        id = await new_comment.insert()
        new_comment.id = id

        # Log and return saved comment object
        logging.debug(f"Comment created in DB: {new_comment}")
        return new_comment

    async def get_all_comments(self) -> List[Comment]:
        # Get all comments from database
        comments = await Comment.all()
        return comments

    async def read_comments(
        self,
        project_name: Optional[str] = None,
        feature_url: Optional[str] = None,
        user_id: Optional[str] = None,
        timestamp_start: Optional[str] = None,
        timestamp_end: Optional[str] = None,
        content_search: Optional[str] = None,
        rating_min: Optional[int] = None,
        rating_max: Optional[int] = None,
    ) -> List[Comment]:
        """
        Get paginated comments from the database that match the given filters.
        Args:
            - project_name: (optional) the name of the project to filter by
            - feature_url: (optional) the feature URL to filter by
            - user_id: (optional) the user ID to filter by
            - timestamp_start: (optional) the earliest timestamp to filter by
            - timestamp_end: (optional) the latest timestamp to filter by
            - content_search: (optional) a search query to filter comments by
            - rating_min: (optional) the minimum rating to filter by
            - rating_max: (optional) the maximum rating to filter by
        Returns:
            A dictionary containing the comments.
        """
        # If no filters are given, return all comments
        if not any(
            (
                project_name,
                feature_url,
                user_id,
                timestamp_start,
                timestamp_end,
                content_search,
                rating_min,
                rating_max,
            )
        ):
            comments = await self.get_all_comments()
            return comments

        else:
            query = []

            if project_name:
                project = await self.get_project_by_name(project_name)
                if project:
                    query.append(Comment.project_id == project.id)
                else:
                    return []

            if feature_url is not None:
                query.append(Comment.feature_url == feature_url)

            if user_id is not None:
                query.append(Comment.user_id == user_id)

            if timestamp_start is not None:
                query.append(Comment.timestamp >= timestamp_start)

            if timestamp_end is not None:
                query.append(Comment.timestamp <= timestamp_end)

            if rating_min is not None:
                query.append(Comment.rating >= rating_min)

            if rating_max is not None:
                query.append(Comment.rating <= rating_max)

            if content_search is None:
                if len(query) == 0:
                    comments = await self.get_all_comments()
                else:
                    query = await Comment.filter(*query)
                    comments = list(query)
            else:
                table = Comment.get_table()
                with Session(Comment.__metadata__.database.engine) as session:
                    result = (
                        session.query(table)
                        .where(table.c.comment.regexp_match(content_search))
                        .all()
                    )
                comments_searched: List[Comment] = Comment.parse_results(
                    result, [], False
                )
                if len(query) == 0:
                    comments = comments_searched
                else:
                    query = await Comment.filter(*query)
                    query_comments = list(query)
                    comments = [x for x in comments_searched if x in query_comments]

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
        self, project_name: str, user_id: str, timestamp: str, feature_url: str
    ) -> Union[Display, None]:
        projects = await Project.filter(name=project_name)

        if len(projects) == 0:
            logging.warning("Project missing on display creation")

            project = await self.create_project(Project(name=project_name))
        else:
            project = projects[0]

        new_display = Display(
            project_id=project.id,
            user_id=user_id,
            timestamp=timestamp,
            feature_url=feature_url,
        )

        id = await new_display.insert()
        new_display.id = id
        logging.debug(f"Display created in DB: {new_display}")
        return new_display


    async def get_rates_from_feature(
            self, 
            feature_url: str,
            timestamp_start: Optional[str] = None, 
            timestamp_end: Optional[str] = None
    )-> Dict[int, List[str]]:
        query=[Comment.feature_url == feature_url]

        if timestamp_start is not None:
            query.append(Comment.timestamp >= timestamp_start)

        if timestamp_end is not None:
            query.append(Comment.timestamp <= timestamp_end)
        comments = await Comment.filter(*query)
        rates_with_timestamps = []

        for comment in comments:
            rate_timestamp = {
                "rate": comment.rating,
                "timestamp": comment.timestamp
            }

            rates_with_timestamps.append(rate_timestamp)

        return rates_with_timestamps
    

    async def filter_rates_by_timerange(
        self, 
        feature_rates, 
        timerange: Optional[str] = "week", 
        timestamp_start: Optional[str] = None, 
        timestamp_end: Optional[str] = None
    ):
        filtered_rates = {}
        
        for feature_url, rates in feature_rates.items():
            filtered_rates[feature_url] = []
            if len(rates) == 0:
                # Handle the case where there are no rates for the feature
                filtered_rates[feature_url] = []

                timestamp=datetime.now()
                timestamp_string = timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f")

                result = self.is_within_timerange(timestamp_string, timerange, timestamp_start, timestamp_end)
                date_timestamp_start= result["date_timestamp_start"] if result["date_timestamp_start"] is not None else None
                date_timestamp_end= result["date_timestamp_end"] if result["date_timestamp_end"] is not None else None
                continue
        
            for rate in rates:
                result = self.is_within_timerange(rate['timestamp'], timerange, timestamp_start, timestamp_end)
                if result["within_range"]:
                    filtered_rates[feature_url].append({
                        "rate": rate["rate"],
                        "date_timestamp": result["date_timestamp"]                        
                    })
                date_timestamp_start= result["date_timestamp_start"] if result["date_timestamp_start"] is not None else None
                date_timestamp_end= result["date_timestamp_end"] if result["date_timestamp_end"] is not None else None

        filtered_rates['date_timestamp_start']=(date_timestamp_start)    
        filtered_rates['date_timestamp_end']=(date_timestamp_end)          
        return filtered_rates


    
    def is_within_timerange(self, timestamp, timerange, timestamp_start, timestamp_end):
        timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
        result={}
        
        if not timestamp_start and not timestamp_end:
            if timerange == "day":
                timestamp_end = datetime.now()
                timestamp_start = timestamp_end.date() - timedelta(days=1)
            elif timerange == "week":
                timestamp_end = datetime.now()
                timestamp_start = timestamp_end.date() - timedelta(weeks=1)
            else:  # month
                timestamp_end = datetime.now()
                timestamp_start = timestamp_end.date() - timedelta(days=30)

            date_timestamp = timestamp.date()
            date_timestamp_start = timestamp_start
            date_timestamp_end = timestamp_end.date()

        elif not timestamp_start:
            if not timestamp_end:
                raise ValueError("Missing timestamp_end.")
            if timerange == "day":
                timestamp_start = datetime.strptime(timestamp_end, "%Y-%m-%d") - timedelta(days=1)
            elif timerange == "week":
                timestamp_start = datetime.strptime(timestamp_end, "%Y-%m-%d") - timedelta(weeks=1)
            else:  # month
                timestamp_start = datetime.strptime(timestamp_end, "%Y-%m-%d") - timedelta(days=30)
            
            date_timestamp = timestamp.date()
            date_timestamp_start = timestamp_start.date()
            date_timestamp_end = datetime.strptime(timestamp_end, "%Y-%m-%d").date()

        elif not timestamp_end:
            if not timestamp_start:
                raise ValueError("Missing timestamp_start.")
            if timerange == "day":
                timestamp_end = datetime.strptime(timestamp_start, "%Y-%m-%d") + timedelta(days=1)
            elif timerange == "week":
                timestamp_end = datetime.strptime(timestamp_start, "%Y-%m-%d") + timedelta(weeks=1)
            else:  # month
                timestamp_end = datetime.strptime(timestamp_start, "%Y-%m-%d") + timedelta(days=30)
            
            date_timestamp = timestamp.date()
            date_timestamp_start = datetime.strptime(timestamp_start, "%Y-%m-%d").date()
            date_timestamp_end = timestamp_end.date()

        else:
            date_timestamp = timestamp.date()
            date_timestamp_start = datetime.strptime(timestamp_start, "%Y-%m-%d").date()
            if timerange == "day":
                date_timestamp_end = date_timestamp_start + timedelta(days=1)
            elif timerange == "week":
                date_timestamp_end = date_timestamp_start + timedelta(days=7)
            else:  # month
                date_timestamp_end = date_timestamp_start + timedelta(days=30)

        result["within_range"] = date_timestamp_start <= date_timestamp <= date_timestamp_end
        result["date_timestamp"] = date_timestamp
        result["date_timestamp_start"] = date_timestamp_start
        result["date_timestamp_end"] = date_timestamp_end
        
        return result
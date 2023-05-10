from typing import List, Optional, Union
import logging

from sqlalchemy.orm import Session
from models.comment import Comment, CommentPostBody
from models.display import Display
from models.project import Project, ProjectEncryption
from utils.encryption import Encryption



class SQLiteRepository:
  
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
            feature_url=comment_body.feature_url,
            user_id=user_id,
            timestamp=timestamp,
            rating=comment_body.rating,
            comment=comment_body.comment,
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
        rating_min:Optional[int] = None,
        rating_max:Optional[int] = None
    ) -> List[Comment]:
        """
        Get all comments from the database that match the given filters.
        Args:
            - project_name: (optional) the name of the project to filter by
            - feature_url: (optional) the feature URL to filter by
            - user_id: (optional) the user ID to filter by
            - timestamp_start: (optional) the earliest timestamp to filter by
            - timestamp_end: (optional) the latest timestamp to filter by
            - content_search: (optional) a search query to filter comments by
        Returns:
            A list of comments that match the given filters
        """
        # print(issubclass(Comment.c.comment,ColumnElement))
        #If no filters are given, return all comments
        if not any((project_name, feature_url, user_id, timestamp_start, timestamp_end, content_search, rating_min, rating_max)):
            return await self.get_all_comments()
        query = []

        print("RATING MIN",rating_min)
        print("RATING MAX",rating_max)
        if project_name :
            project = await self.get_project_by_name(project_name)
            if project : 
                query.append(Comment.project_id==project.id)
            else :
                return []
            
        if feature_url is not None :
            query.append(Comment.feature_url==feature_url) 

        if user_id is not None:
            query.append(Comment.user_id == user_id)

        if timestamp_start is not None :
            query.append(Comment.timestamp >= timestamp_start)

        if timestamp_end is not None:
            query.append(Comment.timestamp <= timestamp_end)

        if rating_min is not None:
            query.append(Comment.rating >=rating_min)

        if rating_max is not None:
            query.append(Comment.rating<=rating_max)

        
        if content_search is None:
            if len(query)==0:
                return await self.get_all_comments()
            else :
                query = await Comment.filter(*query)
                return list(query)
            
        if content_search is not None:
            table = Comment.get_table()
            with Session(Comment.__metadata__.database.engine) as session:
                result = (
                    session.query(table).where(table.c.comment.regexp_match(content_search)).all()
                )
            comments_searched: List[Comment] = Comment.parse_results(result, [], False)
            if len(query)==0:
                return comments_searched
            else :
                query = await Comment.filter(*query)
                print(list(query))
                query_comments = list(query)
                common_comments= [x for x in comments_searched if x in query_comments]
                return common_comments
        
   


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
            project_id = project.id,
            user_id = user_id,
            timestamp = timestamp,
            feature_url = feature_url
        )

        id = await new_display.insert()
        new_display.id = id
        logging.debug(f"Display created in DB: {new_display}")
        return new_display
        

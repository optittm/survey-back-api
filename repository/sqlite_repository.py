from datetime import datetime
from typing import List, Optional, Union
import logging

from models.comment import Comment, CommentPostBody
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
            timestampbegin: Optional[str] = None,
            timestampend: Optional[str] = None,
            search_query: Optional[str] = None,
        ) -> List[Comment]:
        """
        Get all comments from the database that match the given filters.

        Args:
            - project_name: (optional) the name of the project to filter by
            - feature_url: (optional) the feature URL to filter by
            - user_id: (optional) the user ID to filter by
            - timestampbegin: (optional) the earliest timestamp to filter by
            - timestampend: (optional) the latest timestamp to filter by
            - search_query: (optional) a search query to filter comments by

        Returns:
            A list of comments that match the given filters
        """

        # Get all comments from the database
        all_comments = await self.get_all_comments()

        # If no filters are given, return all comments
        if not any((project_name, feature_url, user_id, timestampbegin, timestampend, search_query)):
            return all_comments
        
        # Filter comments by project, feature URL, user ID, timestamp, and search query
        filtered_comments = []
        if project_name is not None:
            project = await self.get_project_by_name(project_name)

            if project is None:
                return filtered_comments
        
            else :
                for comment in all_comments:

                    if project_name and project.id != comment.project_id:
                        continue
                    if feature_url and comment.feature_url != feature_url:
                        continue
                    if user_id and comment.user_id != user_id:
                        continue
                    if timestampbegin:
                        comment_ts = comment.timestamp
                        query_ts = timestampbegin
                        if comment_ts < query_ts:
                            continue
                    if timestampend:
                        comment_ts = comment.timestamp
                        query_ts = timestampend
                        if comment_ts > query_ts:
                            continue
                    if search_query and search_query not in comment.comment:
                        continue
                    filtered_comments.append(comment)
        if project_name is None:
            for comment in all_comments:
                if feature_url and comment.feature_url != feature_url:
                    continue
                if user_id and comment.user_id != user_id:
                    continue
                if timestampbegin:
                    comment_ts = comment.timestamp
                    query_ts = timestampbegin
                    if comment_ts < query_ts:
                        continue
                if timestampend:
                    comment_ts = comment.timestamp
                    query_ts = timestampend
                    if comment_ts > query_ts:
                        continue
                if search_query and search_query not in comment.comment:
                    continue
                filtered_comments.append(comment)
        return filtered_comments


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

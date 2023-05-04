from datetime import datetime
from typing import List, Union
import logging

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
        
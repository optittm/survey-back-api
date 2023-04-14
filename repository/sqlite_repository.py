from datetime import datetime
from typing import List, Union

from models.comment import Comment, CommentPostBody
from models.project import Project, ProjectEncryption
from utils.encryption import Encryption


class SQLiteRepository:
    async def create_comment(
        self,
        commentcookie: CommentPostBody,
        user_id,
        timestamp,
        project_name: str,
    ):
        timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S").isoformat()

        projects = await Project.filter(name=project_name)

        if len(projects) == 0:
            # ajouter une partie qui permet de gérer la clé
            project = await self.create_project(Project(name=project_name))
        else:
            project = projects[0]

        new_comment = Comment(
            project_id=project.id,
            feature_url=commentcookie.feature_url,
            user_id=user_id,
            timestamp=timestamp,
            rating=commentcookie.rating,
            comment=commentcookie.comment,
        )
        id = await new_comment.insert()
        new_comment.id = id
        return new_comment

    async def read_comments(self) -> List[Comment]:
        comments = await Comment.all()
        return comments

    async def create_project(self, project: Project):
        projects = await Project.filter(name=project.name)

        if len(projects) == 0:
            id = await project.insert()
            project.id = id
            projet_encryption = ProjectEncryption(
                project_id=project.id, encryption_key=Encryption.generate_key()
            )
            await projet_encryption.insert()
        else:
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

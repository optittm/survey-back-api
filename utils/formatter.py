from models.comment import Comment, CommentGetBody
from models.project import Project
from dependency_injector.wiring import Provide, inject
from repository.sqlite_repository import SQLiteRepository

from utils.container import Container

async def comment_to_comment_get_body(comment: Comment, sqliterepo: SQLiteRepository = Provide[Container.sqlite_repo]) -> CommentGetBody:
    """
    Convert a Comment to a CommentGetBody with project name
    """
    project: Project = await sqliterepo.get_project_by_id(comment.project_id)
    return CommentGetBody(
        id=comment.id,
        project_name=project.name,
        user_id=comment.user_id,
        timestamp=comment.timestamp,
        feature_url=comment.feature_url,
        rating=comment.rating,
        comment=comment.comment,
    )
from models.comment import Comment, CommentGetBody
from models.project import Project
from dependency_injector.wiring import Provide
from repository.sqlite_repository import SQLiteRepository
import logging

from utils.container import Container


def str_to_bool(string: str):
    if string.lower() == "true":
        return True
    elif string.lower() == "false":
        return False
    else:
        logging.error(f"String value {string} cannot be converted to bool")
        raise Exception(f"String value {string} cannot be converted to bool")


async def comment_to_comment_get_body(
    comment: Comment, sqliterepo: SQLiteRepository = Provide[Container.sqlite_repo]
) -> CommentGetBody:
    """
    Convert a Comment to a CommentGetBody with project name
    """
    project: Project = await sqliterepo.get_project_by_id(comment.project_id)
    new_comment = CommentGetBody(
        id=comment.id,
        project_name=project.name,
        user_id=comment.user_id,
        timestamp=comment.timestamp,
        feature_url=comment.feature_url,
        rating=comment.rating,
        comment=comment.comment,
        language=comment.language,
        sentiment=comment.sentiment,
        sentiment_score=comment.sentiment_score,
    )
    logging.debug(f"Formatted comment object to {new_comment}")
    return new_comment

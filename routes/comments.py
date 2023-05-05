from typing import List, Union
from fastapi import APIRouter, Depends, status, Cookie, Response
from dependency_injector.wiring import Provide, inject
from datetime import datetime, timedelta
import logging

from models.comment import Comment, CommentGetBody, CommentPostBody
from models.rule import Rule
from utils.container import Container
from repository.sqlite_repository import SQLiteRepository
from repository.yaml_rule_repository import YamlRulesRepository
from utils.encryption import Encryption
from utils.formatter import comment_to_comment_get_body
from utils.middleware import comment_body_treatment

router = APIRouter()


@router.post(
    "/comments",
    status_code=status.HTTP_201_CREATED,
    response_model=Union[Comment, dict],
)
@inject
async def create_comment(
    response: Response,
    comment_body: CommentPostBody = Depends(comment_body_treatment),
    user_id: Union[str, None] = Cookie(default=None),
    timestamp: Union[str, None] = Cookie(default=None),
    sqlite_repo: SQLiteRepository = Depends(Provide[Container.sqlite_repo]),
    rules_config: YamlRulesRepository = Depends(Provide[Container.rules_config]),
) -> Comment:
    if (
        project_name := rules_config.getProjectNameFromFeature(comment_body.feature_url)
    ) is not None:
        if user_id is None or timestamp is None:
            logging.error("POST comments::Missing cookies")
            response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            return {"Error": "Missing cookies"}

        # Retrieve the encryption key of the project
        project = await sqlite_repo.get_project_by_name(project_name)
        encryption_db = await sqlite_repo.get_encryption_by_project_id(project.id)
        encryption = Encryption(encryption_db.encryption_key)

        # Decrypt timestamp
        try:
            decrypted_timestamp = encryption.decrypt(timestamp)
        except Exception:
            logging.error("POST comments::Invalid timestamp, cannot decrypt")
            response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            return {"Error": "Invalid timestamp, cannot decrypt"}

        dt_timestamp = datetime.fromtimestamp(float(decrypted_timestamp))
        # Check delay to answer
        rule: Rule = rules_config.getRuleFromFeature(comment_body.feature_url)
        if (datetime.now() - dt_timestamp) >= timedelta(minutes=rule.delay_to_answer):
            response.status_code = status.HTTP_408_REQUEST_TIMEOUT
            return {"Error": "Time to submit a comment has elapsed"}

        iso_timestamp = dt_timestamp.isoformat()
        new_comment = await sqlite_repo.create_comment(
            comment_body, user_id, iso_timestamp, project_name
        )
        return new_comment
    else:
        logging.error("POST comments::Feature not found")
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"Error": "Feature not found"}


@router.get("/comments", response_model=List[CommentGetBody])
@inject
async def get_all_comments(
    sqlite_repo: SQLiteRepository = Depends(Provide[Container.sqlite_repo]),
) -> List[Comment]:
    comments = await sqlite_repo.read_comments()
    comments = [await comment_to_comment_get_body(comment) for comment in comments]
    return comments

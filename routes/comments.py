from typing import List, Union
from fastapi import APIRouter, Depends, status, Cookie, Response
from dependency_injector.wiring import Provide, inject
from datetime import datetime

from models.comment import Comment, CommentGetBody, CommentPostBody
from utils.container import Container
from repository.sqlite_repository import SQLiteRepository
from repository.yaml_rule_repository import YamlRulesRepository
from utils.encryption import Encryption
from utils.formatter import comment_to_comment_get_body

router = APIRouter()


@router.post(
    "/comments",
    status_code=status.HTTP_201_CREATED,
    response_model=Union[Comment, dict],
)
@inject
async def create_comment(
    comment_body: CommentPostBody,
    response: Response,
    user_id: Union[str, None] = Cookie(default=None),
    timestamp: Union[str, None] = Cookie(default=None),
    sqlite_repo: SQLiteRepository = Depends(Provide[Container.sqlite_repo]),
    rules_config: YamlRulesRepository = Depends(Provide[Container.rules_config]),
) -> Comment:
    if (
        project_name := rules_config.getProjectNameFromFeature(comment_body.feature_url)
    ) is not None:
        if user_id is None or timestamp is None:
            response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            return {"Error": "Missing cookies"}

        # Retrieve the encryption key of the project
        project = await sqlite_repo.get_project_by_name(project_name)
        encryption_db = await sqlite_repo.get_encryption_by_project_id(project.id)
        encryption = Encryption(encryption_db.encryption_key)
        # Decrypt and convert to ISO 6801
        decrypted_timestamp = encryption.decrypt(timestamp)
        iso_timestamp = datetime.fromtimestamp(float(decrypted_timestamp)).isoformat()

        new_comment = await sqlite_repo.create_comment(
            comment_body, user_id, iso_timestamp, project_name
        )
        return new_comment
    else:
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

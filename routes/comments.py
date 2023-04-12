from typing import List, Union
from fastapi import APIRouter, Depends, status, Cookie, Response
from dependency_injector.wiring import Provide, inject

from models.comment import Comment, CommentGetBody, CommentPostBody
from utils.container import Container
from repository.sqlite_repository import SQLiteRepository
from repository.yaml_rule_repository import YamlRulesRepository
from utils.formatter import comment_to_comment_get_body

router = APIRouter()

@router.post("/comments", status_code=status.HTTP_201_CREATED, response_model=Union[Comment, dict])
@inject
async def create_comment(
        comment_body: CommentPostBody,
        response: Response,
        user_id: Union[str, None] = Cookie(default=None),
        timestamp: Union[str, None] = Cookie(default=None),
        sqlite_repo: SQLiteRepository = Depends(Provide[Container.sqlite_repo]),
        rules_config: YamlRulesRepository = Depends(Provide[Container.rules_config])
    ) -> Comment:

    if (project_name := rules_config.getProjectNameFromFeature(comment_body.feature_url)) is not None:
        new_comment = await sqlite_repo.create_comment(comment_body, user_id, timestamp, project_name)
        return new_comment
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"Error": "Feature not found"}

@router.get("/comments",  response_model=List[CommentGetBody])
@inject
async def get_all_comments(sqlite_repo: SQLiteRepository = Depends(Provide[Container.sqlite_repo])) -> List[Comment]:
    comments = await sqlite_repo.read_comments()
    comments = [await comment_to_comment_get_body(comment) for comment in comments]
    return comments
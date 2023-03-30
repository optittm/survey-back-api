from typing import List, Union
from fastapi import APIRouter, Depends, status, Cookie
from dependency_injector.wiring import Provide, inject

from models.comment import Comment, CommentPostBody
from utils.container import Container
from repository.sqlite_repository import SQLiteRepository

router = APIRouter()

@router.post("/comments", status_code=status.HTTP_201_CREATED,response_model=Comment)
@inject
async def create_comment(
        comment_body: CommentPostBody,
        user_id: Union[str, None] = Cookie(default=None),
        timestamp: Union[str, None] = Cookie(default=None),
        sqlite_repo: SQLiteRepository = Depends(Provide[Container.sqlite_repo])
    ) -> Comment:
    # TODO: get domain name from request instead
    project_name = comment_body.feature_url.split('/')[2]
    new_comment = await sqlite_repo.create_comment(comment_body, user_id, timestamp, project_name)
    return new_comment

@router.get("/comments",  response_model=List[Comment])
@inject
async def get_all_comments(sqlite_repo: SQLiteRepository = Depends(Provide[Container.sqlite_repo])) -> List[Comment]:
    comments = await sqlite_repo.read_comments()
    return comments
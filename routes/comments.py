from typing import Annotated, List
from databases import Database
from fastapi import APIRouter, Depends, HTTPException, Request, status, Cookie
from pytest import console_main
from models.comment import Comment
from models.project import Project
from utils.container import Container
from dependency_injector.wiring import Provide, inject
from repository.DBrepository import CommentRepository
from models.commentcookie import CommentCookie
router = APIRouter()

@router.post("/comments", status_code=status.HTTP_201_CREATED,response_model=Comment)
@inject
async def create_comment(commentcookie: CommentCookie, user_id: str | None= Cookie(default=None), timestamp: str | None=Cookie(default=None),comment_repo: CommentRepository = Depends(Provide[Container.db_manager])) -> Comment:
    project_name = commentcookie.feature_url.split('/')[2]
    new_comment = await comment_repo.create_comment(commentcookie, user_id, timestamp, project_name)
    return new_comment

@router.get("/comments",  response_model=List[Comment])
@inject
async def get_all_comments(comment_repo: CommentRepository = Depends(Provide[Container.db_manager])) ->List[Comment]:
    comments = await comment_repo.read_comments()
    return comments
from typing import List
from databases import Database
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, status
from models.comment import Comment
from utils.container import Container
from dependency_injector.wiring import Provide, inject
from repository.DBrepository import CommentRepository

router = APIRouter()

@router.post("/comments", status_code=status.HTTP_201_CREATED,response_model=Comment)
@inject
async def create_comment(comment: Comment, comment_repo: CommentRepository = Depends(Provide[Container.db_manager])) -> Comment:
    new_comment =comment_repo.create_comment(comment)
    return new_comment

@router.get("/comments",  response_model=List[Comment])
@inject
async def get_all_comments(comment_repo: CommentRepository = Depends(Provide[Container.db_manager])) ->List[Comment]:
    comments = await comment_repo.read_comments()
    return comments
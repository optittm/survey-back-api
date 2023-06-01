from math import ceil
from typing import Any, Optional, Union, Dict
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
from utils.nlp import text_preprocess


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
    config=Depends(Provide[Container.config]),
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

        # Sentiment analysis
        if len(comment_body.comment):
            word_tokens = text_preprocess(comment_body.comment)
            # TODO analysis from tokens

        iso_timestamp = dt_timestamp.isoformat()
        new_comment = await sqlite_repo.create_comment(
            comment_body.feature_url,
            comment_body.rating,
            comment_body.comment,
            # Depending on config, use either the fingerprint passed in body, or the UUID from cookie
            comment_body.user_id if config["use_fingerprint"] else user_id,
            iso_timestamp,
            project_name,
        )
        return new_comment
    else:
        logging.error("POST comments::Feature not found")
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"Error": "Feature not found"}


@router.get("/comments", response_model=Dict[str, Any])
@inject
async def get_comments(
    project_name: Optional[str] = None,
    feature_url: Optional[str] = None,
    user_id: Optional[str] = None,
    timestamp_start: Optional[str] = None,
    timestamp_end: Optional[str] = None,
    content_search: Optional[str] = None,
    rating_min: Optional[int] = None,
    rating_max: Optional[int] = None,
    page: Optional[int] = 1,
    page_size: Optional[int] = 20,
    sqlite_repo: SQLiteRepository = Depends(Provide[Container.sqlite_repo])
) -> Dict[str, Any]:
    
    comments = await sqlite_repo.read_comments(
        project_name=project_name,
        feature_url=feature_url,
        user_id=user_id,
        timestamp_start=timestamp_start,
        timestamp_end=timestamp_end,
        content_search=content_search,
        rating_min=rating_min,
        rating_max=rating_max
    )
    # Perform pagination
    total_comments = len(comments)
    total_pages = ceil(total_comments / page_size)
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    paginated_comments = comments[start_index:end_index]

    commentsreturn = [await comment_to_comment_get_body(comment) for comment in paginated_comments]

    # Prepare pagination information
    next_page = f"/comments?page={page + 1}&pageSize={page_size}" if page < total_pages else None
    prev_page = f"/comments?page={page - 1}&pageSize={page_size}" if page > 1 else None

    return { 
            "results": commentsreturn,
            "page": page,
            "page_size": page_size,
            "total_comments": total_comments,
            "total_pages": total_pages,
            "next_page": next_page,
            "prev_page": prev_page,
    }
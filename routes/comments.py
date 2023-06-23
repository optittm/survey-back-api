from typing import Optional
from fastapi import APIRouter, Depends, Security, status, Cookie, Request
from models.pagination import Pagination

from survey_logic import comments as logic
from models.comment import Comment, CommentPostBody
from models.security import ScopeEnum
from utils.formatter import comment_to_comment_get_body, paginate_results
from routes.middlewares.feature_url import comment_body_treatment, remove_search_hash_from_url
from routes.middlewares.security import check_jwt


router = APIRouter()


@router.post(
    "/comments",
    dependencies=[Security(check_jwt, scopes=[ScopeEnum.CLIENT.value])],
    status_code=status.HTTP_201_CREATED,
    response_model=Comment,
)
async def create_comment(
    comment_body: CommentPostBody = Depends(comment_body_treatment),
    user_id: Optional[str] = Cookie(default=None),
    timestamp: Optional[str] = Cookie(default=None),
) -> Comment:
    return await logic.create_comment(
        comment_body.feature_url,
        comment_body.rating,
        comment_body.comment,
        comment_body.user_id,
        user_id,
        timestamp,
    )


@router.get(
    "/comments",
    dependencies=[Security(check_jwt, scopes=[ScopeEnum.DATA.value])],
    response_model=Pagination[Comment],
)
async def get_comments(
    request: Request,
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
) -> Pagination[Comment]:
    comments = await logic.get_comments(
        project_name=project_name,
        feature_url=feature_url,
        user_id=user_id,
        timestamp_start=timestamp_start,
        timestamp_end=timestamp_end,
        content_search=content_search,
        rating_min=rating_min,
        rating_max=rating_max,
    )
    
    if not any([
        project_name,
        feature_url,
        user_id,
        timestamp_start,
        timestamp_end,
        content_search,
        rating_min,
        rating_max,
    ]):
        filters = None
    else:
        # Writes the filters used in the request, apart from the pagination ones
        filters = {}
        queries = request.url.query.split("&")
        for query in queries:
            k, v = query.split("=")
            if k in ["page", "page_size"]:
                continue
            filters[k] = v

    pagination = paginate_results(
        all_values=comments,
        page_size=page_size,
        page=page,
        resource_url=remove_search_hash_from_url(str(request.url)),
        request_filters=filters,
    )
    pagination.results = [
        await comment_to_comment_get_body(comment) for comment in pagination.results
    ]
    return pagination

    

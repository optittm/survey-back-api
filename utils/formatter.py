from math import ceil
from typing import Dict, List, Optional, TypeVar, Union
from models.comment import Comment, CommentGetBody
from models.project import Project
from dependency_injector.wiring import Provide, inject
from repository.sqlite_repository import SQLiteRepository
import logging

from utils.container import Container
from utils.nlp import NlpPreprocess
from models.pagination import Pagination


def str_to_bool(string: str):
    if string.lower() == "true":
        return True
    elif string.lower() == "false":
        return False
    else:
        logging.error(f"String value {string} cannot be converted to bool")
        raise Exception(f"String value {string} cannot be converted to bool")

@inject
async def comment_to_comment_get_body(
    comment: Comment,
    sqliterepo: SQLiteRepository = Provide[Container.sqlite_repo],
    nlp_preprocess: NlpPreprocess = Provide[Container.nlp_preprocess],
) -> CommentGetBody:
    """
    Convert a Comment to a CommentGetBody with project name
    """
    project: Project = await sqliterepo.get_project_by_id(comment.project_id)
    try:
        processed_text = nlp_preprocess.text_preprocess(comment.comment, comment.language)
    except NotImplementedError:
        logging.error(f"Could not preprocess text of language {comment.language}")
        logging.debug(f"Unable to do NLP preprocess on this text: {comment.comment}")
        processed_text = None
    
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
        comment_nlp=processed_text,
    )
    logging.debug(f"Formatted comment object to {new_comment}")
    return new_comment

T = TypeVar("T")

def paginate_results(
    all_values: List[T],
    page_size: int,
    page: int,
    resource_url: str,
    request_filters: Optional[Dict[str, Union[str, int]]] = None,
) -> Pagination[T]:
    """
    Create a paginated result from the full list of items

    Args:
        - all_values: the full list of items to slice into pages
        - page_size: the number of items to display in one page
        - page: the number of the page to return
        - resource_url: the URL of the request without the query string
        - request_filters: a dictionary representing the additional params in the request URL, apart from page and page_size
    
    Returns:
        A Pagination object reprensenting the page to return
    """

    if page_size < 1 or page < 1:
        raise ValueError("Invalid page or page size")

    total = len(all_values)
    if total > 0:
        total_pages = ceil(total / page_size)
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        page_of_values = all_values[start_index:end_index]
    else:
        total_pages = 1
        page_of_values = []

    return Pagination.paginate(
        results=page_of_values,
        page=page,
        total=total,
        total_pages=total_pages,
        resource_url=resource_url,
        request_filters=request_filters,
        page_size=page_size,
    )
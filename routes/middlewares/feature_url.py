import logging
from urllib.parse import urlsplit
from fastapi import HTTPException, status

from models.comment import CommentPostBody


def remove_search_hash_from_url(featureUrl: str):
    """
    Removes the search part (starting with ?)
    and the hash part (starting with #) from a given URL
    """
    try:
        split_url = urlsplit(featureUrl)
    except Exception:
        logging.error("Feature URL middleware::Invalid feature URL")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid feature URL",
        )
    split_url = split_url._replace(query="", fragment="")
    return split_url.geturl()


def comment_body_treatment(comment_body: CommentPostBody):
    comment_body.feature_url = remove_search_hash_from_url(comment_body.feature_url)
    return comment_body

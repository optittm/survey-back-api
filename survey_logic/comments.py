from typing import List, Optional
from fastapi import Depends, status, HTTPException
from dependency_injector.wiring import Provide, inject
from datetime import datetime, timedelta
import logging

from models.comment import Comment
from models.rule import Rule
from survey_logic.projects import get_encryption_from_project_name
from utils.container import Container
from repository.sqlite_repository import SQLiteRepository
from repository.yaml_rule_repository import YamlRulesRepository
from utils.nlp import SentimentAnalysis, detect_language

@inject
async def create_comment(
    feature_url: str,
    rating: int,
    comment: str,
    fingerprint_user_id: str,
    cookie_user_id: Optional[str] = None,
    timestamp: Optional[str] = None,
    sqlite_repo: SQLiteRepository = Depends(Provide[Container.sqlite_repo]),
    rules_config: YamlRulesRepository = Depends(Provide[Container.rules_config]),
    sentiment_analysis: SentimentAnalysis = Depends(Provide[Container.sentiment_analysis]),
    config = Depends(Provide[Container.config]),
) -> Comment:
    
    if (
        project_name := rules_config.getProjectNameFromFeature(feature_url)
    ) is None:
        logging.error("create_comment::Feature not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature not found",
        )
    
    if cookie_user_id is None or timestamp is None:
        logging.error("create_comment::Missing cookies")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Missing cookies",
        )
    
    encryption = await get_encryption_from_project_name(project_name)

    # Decrypt timestamp
    try:
        decrypted_timestamp = encryption.decrypt(timestamp)
    except Exception:
        logging.error("create_comment::Invalid timestamp, cannot decrypt")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid timestamp, cannot decrypt",
        )

    dt_timestamp = datetime.fromtimestamp(float(decrypted_timestamp))
    # Check delay to answer
    rule: Rule = rules_config.getRuleFromFeature(feature_url)
    if (datetime.now() - dt_timestamp) >= timedelta(minutes=rule.delay_to_answer):
        logging.error("create_comment::Time to submit a comment has elapsed")
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail="Time to submit a comment has elapsed",
        )

    # Sentiment analysis
    if len(comment):
        language = detect_language(comment)
        try:
            sentiment, score = sentiment_analysis.analyze(comment, language)
        except Exception:
            logging.error(f"Could not analyze sentiment of comment of language {language}")
            logging.debug(f"Unable to do sentiment analysis on this comment: {comment}")
            sentiment, score = None, None
    else:
        sentiment, score = None, None

    iso_timestamp = dt_timestamp.isoformat()
    new_comment = await sqlite_repo.create_comment(
        feature_url,
        rating,
        comment,
        # Depending on config, use either the fingerprint passed in body, or the UUID from cookie
        fingerprint_user_id if config["use_fingerprint"] else cookie_user_id,
        iso_timestamp,
        project_name,
        language,
        sentiment,
        score,
    )
    return new_comment

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
    sqlite_repo: SQLiteRepository = Depends(Provide[Container.sqlite_repo]),
) -> List[Comment]:
    comments = await sqlite_repo.read_comments(
        project_name=project_name,
        feature_url=feature_url,
        user_id=user_id,
        timestamp_start=timestamp_start,
        timestamp_end=timestamp_end,
        content_search=content_search,
        rating_min=rating_min,
        rating_max=rating_max,
    )
    return comments
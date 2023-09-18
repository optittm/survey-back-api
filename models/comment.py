from enum import Enum
from typing import Optional, List
from pydantic import validator
from pydbantic import DataBaseModel, PrimaryKey, ForeignKey
from datetime import datetime
import logging
from models.project import Project

class SentimentEnum(Enum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"


class CommentPostBody(DataBaseModel):
    """
    Comment model for validating the body received on POST request
    """

    feature_url: str
    rating: int
    comment: str
    user_id: str

    @validator("rating")
    def validate_rating(cls, value):
        if not 1 <= value <= 5:
            logging.error("Rating value is out of range")
            raise ValueError("Rating must be an integer between 1 and 5")
        return value


class CommentCommon(CommentPostBody):
    """
    Intermediary class, for code organization purposes only
    """

    id: Optional[int] = PrimaryKey(autoincrement=True)
    timestamp: str
    language: str # two-character ISO639-1 code
    sentiment: Optional[str]
    sentiment_score: Optional[float]

    @validator("timestamp")
    def encode_timestamp(cls, value):
        try:
            datetime.fromisoformat(value)
        except ValueError:
            raise ValueError("Invalid timestamp format")
        return value


class Comment(CommentCommon):
    """
    Comment model for the SQL table
    """

    project_id: int = ForeignKey(Project, "id")


class CommentGetBody(CommentCommon):
    """
    Comment model for sending on GET request
    """

    project_name: str
    comment_nlp: Optional[List[str]] # Pre-processed version of the comment for NLP purposes

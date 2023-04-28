from typing import Optional
from pydantic import validator
from pydbantic import DataBaseModel, PrimaryKey, ForeignKey
from datetime import datetime
import logging
from models.project import Project


class Comment(DataBaseModel):
    """
    Comment model for the SQL table
    """

    id: Optional[int] = PrimaryKey(autoincrement=True)
    project_id: int = ForeignKey(Project, "id")
    user_id: str
    timestamp: str
    feature_url: str
    rating: int
    comment: str

    @validator("rating")
    def validate_rating(cls, value):
        if not 1 <= value <= 5:
            logging.error("Rating value is out of range")
            raise ValueError("Rating must be an integer between 1 and 5")
        return value

    @validator("timestamp")
    def encode_timestamp(cls, value):
        try:
            datetime.fromisoformat(value)
        except ValueError:
            raise ValueError("Invalid timestamp format")
        return value


class CommentPostBody(DataBaseModel):
    """
    Comment model for validating the body received on POST request
    """

    feature_url: str
    rating: int
    comment: str

    @validator("rating")
    def validate_rating(cls, value):
        if not 1 <= value <= 5:
            logging.error("Rating value is out of range")
            raise ValueError("Rating must be an integer between 1 and 5")
        return value


class CommentGetBody(DataBaseModel):
    """
    Comment model for sending on GET request
    """

    id: Optional[int] = PrimaryKey(autoincrement=True)
    project_name: str
    user_id: str
    timestamp: str
    feature_url: str
    rating: int
    comment: str

    @validator("rating")
    def validate_rating(cls, value):
        if not 1 <= value <= 5:
            logging.error("Rating value is out of range")
            raise ValueError("Rating must be an integer between 1 and 5")
        return value

    @validator("timestamp")
    def encode_timestamp(cls, value):
        try:
            datetime.fromisoformat(value)
        except ValueError:
            raise ValueError("Invalid timestamp format")
        return value

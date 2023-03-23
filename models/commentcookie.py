from pydantic import validator
from pydbantic import DataBaseModel

class CommentCookie(DataBaseModel):
    feature_url: str
    rating: int
    comment: str

    @validator("rating")
    def validate_rating(cls, value):
        if not 1 <= value <= 5:
            raise ValueError("Rating must be an integer between 1 and 5")
        return value
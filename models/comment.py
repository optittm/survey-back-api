from typing import Optional
from pydantic import validator
from pydbantic import DataBaseModel, PrimaryKey, ForeignKey
from datetime import datetime
from models.project import Project

class Comment(DataBaseModel):
    id: Optional[int] = PrimaryKey(autoincrement=True)
    project_id: int= ForeignKey(Project, "id")
    user_id: str
    timestamp: datetime
    feature_url: str
    rating: int
    comment: str

    @validator("rating")
    def validate_rating(cls, value):
        if not 1 <= value <= 5:
            raise ValueError("Rating must be an integer between 1 and 5")
        return value
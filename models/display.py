from datetime import datetime
from typing import Optional
from pydantic import validator
from models.project import Project
from pydbantic import DataBaseModel, PrimaryKey, ForeignKey

class Display(DataBaseModel):
    """
    Comment model for the SQL table
    """

    id: Optional[int] = PrimaryKey(autoincrement=True)
    project_id: int = ForeignKey(Project, "id")
    user_id: str
    timestamp: str
    feature_url: str

    @validator("timestamp")
    def encode_timestamp(cls, value):
        try:
            datetime.fromisoformat(value)
        except ValueError:
            raise ValueError("Invalid timestamp format")
        return value
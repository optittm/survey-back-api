from pydbantic import DataBaseModel, PrimaryKey, Unique
from datetime import datetime

class Comment(DataBaseModel):
    id: int = PrimaryKey()
    project_name: str
    feature_url: str
    user_id: str
    timestamp: datetime
    rating: int
    comment: str
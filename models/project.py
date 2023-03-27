from typing import Optional
from pydbantic import DataBaseModel, PrimaryKey, Unique
from datetime import datetime

class Project(DataBaseModel):
    id: Optional[int] = PrimaryKey(autoincrement=True)
    name: str= Unique()
    
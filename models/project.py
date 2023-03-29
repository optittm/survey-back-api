from typing import Optional
from pydbantic import DataBaseModel, PrimaryKey, Unique

class Project(DataBaseModel):
    id: Optional[int] = PrimaryKey(autoincrement=True)
    name: str = Unique()
    
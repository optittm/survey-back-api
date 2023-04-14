from typing import Optional
from pydbantic import DataBaseModel, PrimaryKey, Unique, ForeignKey


class Project(DataBaseModel):
    id: Optional[int] = PrimaryKey(autoincrement=True)
    name: str = Unique()


class ProjectEncryption(DataBaseModel):
    id: Optional[int] = PrimaryKey(autoincrement=True)
    project_id: int = ForeignKey(Project, "id")
    encryption_key: str

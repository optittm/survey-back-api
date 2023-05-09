
from typing import List
from fastapi import APIRouter, Depends

from dependency_injector.wiring import Provide, inject
from models.project import Project
from repository.sqlite_repository import SQLiteRepository
from repository.yaml_rule_repository import YamlRulesRepository
from utils.container import Container

router = APIRouter()

@router.get("/projects", response_model=List)
@inject
async def get_projects(
    sqlite_repo: SQLiteRepository = Depends(Provide[Container.sqlite_repo]),
    yaml_repo: YamlRulesRepository = Depends(Provide[Container.rules_config])
) -> List:  
    """
    Retrieve a list of projects with their respective ids and names.
    
    Args:
        sqlite_repo (SQLiteRepository, optional): The SQLiteRepository instance to use for database access.
            Defaults to Depends(Provide[Container.sqlite_repo]).
        yaml_repo (YamlRulesRepository, optional): The YamlRulesRepository instance to use for rules configuration.
            Defaults to Depends(Provide[Container.rules_config]).
    
    Returns:
        List[dict]: A list of dictionaries containing the id and name of each project.
    """
    output = []
    for name in yaml_repo.getProjectNames():
        project = await sqlite_repo.get_project_by_name(name)
        if not project:
            project = await sqlite_repo.create_project(Project(name = name))
        output.append({"id": project.id, "name": project.name})
    return output
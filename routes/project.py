
from typing import List, Union
from fastapi import APIRouter, Depends

from dependency_injector.wiring import Provide, inject
from models.project import Project
from repository.sqlite_repository import SQLiteRepository
from repository.yaml_rule_repository import YamlRulesRepository
from utils.container import Container

router = APIRouter()

@router.get("/projects/{id}/feature_rating", response_model=Union[List, dict])
@inject
async def get_projects_feature_rating(
    id: int,
    sqlite_repo: SQLiteRepository = Depends(Provide[Container.sqlite_repo]),
    yaml_repo: YamlRulesRepository = Depends(Provide[Container.rules_config])
) -> List:  
    """
    Returns the feature ratings for a given project ID.

    Args:
        id (int): The ID of the project to retrieve feature ratings for.
        sqlite_repo (SQLiteRepository, optional): The SQLite repository to retrieve data from.
            Defaults to Depends(Provide[Container.sqlite_repo]).
        yaml_repo (YamlRulesRepository, optional): The YAML repository to retrieve data from.
            Defaults to Depends(Provide[Container.rules_config]).

    Returns:
        List: A list of dictionaries containing the feature URL and rating for the specified project.
            If the project is not found, returns a dictionary with the error message.
    """
    output = []
    project = await sqlite_repo.get_project_by_id(id)
    if not project or project.name not in yaml_repo.getProjectNames():
        return {"id": id, "Error": "Project not found"}
    feature_urls = yaml_repo.getFeatureUrlsFromProjectName(project.name)
    for url in feature_urls:
        output.append({
            "url": url, 
            "rating": sqlite_repo.get_feature_avg_rating(project.id, url)
        })
    return output
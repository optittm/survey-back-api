
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
) -> Union[List, dict]:  
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


@router.get("/projects/{id}/rules", response_model=Union[List, dict])
@inject
async def get_projects_rules(
    id: int,
    sqlite_repo: SQLiteRepository = Depends(Provide[Container.sqlite_repo]),
    yaml_repo: YamlRulesRepository = Depends(Provide[Container.rules_config])
) -> Union[List, dict]:  
    """
    Returns the rules for a project with the given ID.

    Args:
        id (int): the ID of the project to retrieve rules for
        sqlite_repo (SQLiteRepository): the SQLite repository to use for accessing project information
        yaml_repo (YamlRulesRepository): the YAML repository to use for accessing rule information

    Returns:
        Union[List, dict]: a list of rules for the project, or an error dictionary if the project is not found
    """
    output = []
    project = await sqlite_repo.get_project_by_id(id)
    if not project or project.name not in yaml_repo.getProjectNames():
        return {"id": id, "Error": "Project not found"}
    feature_urls = yaml_repo.getFeatureUrlsFromProjectName(project.name)
    for url in feature_urls:
        rule = yaml_repo.getRuleFromFeature(url)
        output.append({
            "url": rule.feature_url,
            "ratio": rule.ratio,
            "delay_before_reanswer": rule.delay_before_reanswer,
            "delay_to_answer": rule.delay_to_answer,
            "is_active": rule.is_active
            
        })
    return output
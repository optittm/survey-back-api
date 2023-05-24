import logging
from typing import List, Union
from fastapi import APIRouter, Depends, HTTPException, Security, status

from dependency_injector.wiring import Provide, inject
from models.project import Project
from models.rule import Rule
from models.security import ScopeEnum

from repository.sqlite_repository import SQLiteRepository
from repository.yaml_rule_repository import YamlRulesRepository
from routes.middlewares.security import check_jwt
from utils.container import Container

router = APIRouter()


@router.get(
    "/projects",
    dependencies=[Security(check_jwt, scopes=[ScopeEnum.DATA.value])],
    response_model=List,
)
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


@router.get(
    "/project/{id}/avg_feature_rating",
    dependencies=[Security(check_jwt, scopes=[ScopeEnum.DATA.value])],
    response_model=Union[List, dict],
)
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
        logging.error("Project not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"id": id, "Error": "Project not found"},
        )
    feature_urls = yaml_repo.getFeatureUrlsFromProjectName(project.name)
    for url in feature_urls:
        output.append({
            "url": url, 
            "rating": sqlite_repo.get_feature_avg_rating(project.id, url)
        })
    return output


@router.get(
    "/projects/{id}/rules",
    dependencies=[Security(check_jwt, scopes=[ScopeEnum.DATA.value])],
    response_model=Union[List, Rule],
)
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
        logging.error("Project not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"id": id, "Error": "Project not found"},
        )
    feature_urls = yaml_repo.getFeatureUrlsFromProjectName(project.name)
    for url in feature_urls:
        rule = yaml_repo.getRuleFromFeature(url)
        output.append(rule)
    return output


@router.get(
    "/project/{id}/avg_rating",
    dependencies=[Security(check_jwt, scopes=[ScopeEnum.DATA.value])],
    response_model=dict,
)
@inject
async def get_project_rating(
    id: int,
    sqlite_repo: SQLiteRepository = Depends(Provide[Container.sqlite_repo]),
    yaml_repo: YamlRulesRepository = Depends(Provide[Container.rules_config])
) -> dict:  
    """
    Retrieve the average rating of a project with the given id.
    
    Args:
        id (int): The id of the project to retrieve the rating for.
        sqlite_repo (SQLiteRepository, optional): The SQLiteRepository instance to use for database access.
            Defaults to Depends(Provide[Container.sqlite_repo]).
        yaml_repo (YamlRulesRepository, optional): The YamlRulesRepository instance to use for rules configuration.
            Defaults to Depends(Provide[Container.rules_config]).
    
    Returns:
        dict: A dictionary containing the project id and its average rating, or an error message if the project
        was not found or if its name is not included in the list of project names in the YamlRulesRepository.
    """

    project = await sqlite_repo.get_project_by_id(id)
    if not project or project.name not in yaml_repo.getProjectNames():
        logging.error("Project not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"id": id, "Error": "Project not found"},
        )
    rating = sqlite_repo.get_project_avg_rating(id)
    return {
        "id": id,
        "rating": rating
    }


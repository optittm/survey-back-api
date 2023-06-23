import logging
from typing import List
from fastapi import Depends, HTTPException, status
from dependency_injector.wiring import Provide, inject

from models.project import Project
from models.rule import Rule
from repository.sqlite_repository import SQLiteRepository
from repository.yaml_rule_repository import YamlRulesRepository
from utils.container import Container
from utils.encryption import Encryption

@inject
async def get_encryption_from_project_name(
    project_name: str,
    sqlite_repo: SQLiteRepository = Depends(Provide[Container.sqlite_repo]),
) -> Encryption:
    # Retrieve the encryption key of the project
    project = await sqlite_repo.get_project_by_name(project_name)
    encryption_db = await sqlite_repo.get_encryption_by_project_id(project.id)
    encryption = Encryption(encryption_db.encryption_key)
    return encryption

@inject
async def get_all_projects(
    sqlite_repo: SQLiteRepository = Depends(Provide[Container.sqlite_repo]),
    yaml_repo: YamlRulesRepository = Depends(Provide[Container.rules_config]),
) -> List[dict]:
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
            project = await sqlite_repo.create_project(Project(name=name))
        output.append({"id": project.id, "name": project.name})
    return output

@inject
async def get_avg_rating_by_feature_from_project_id(
    project_id: int,
    sqlite_repo: SQLiteRepository = Depends(Provide[Container.sqlite_repo]),
    yaml_repo: YamlRulesRepository = Depends(Provide[Container.rules_config]),
) -> List[dict]:
    """
    Returns the feature ratings for a given project ID.

    Args:
        project_id (int): The ID of the project to retrieve feature ratings for.
        sqlite_repo (SQLiteRepository, optional): The SQLite repository to retrieve data from.
            Defaults to Depends(Provide[Container.sqlite_repo]).
        yaml_repo (YamlRulesRepository, optional): The YAML repository to retrieve data from.
            Defaults to Depends(Provide[Container.rules_config]).

    Returns:
        List: A list of dictionaries containing the feature URL and rating for the specified project.
            If the project is not found, returns a dictionary with the error message.
    """
    output = []
    project = await sqlite_repo.get_project_by_id(project_id)
    if not project or project.name not in yaml_repo.getProjectNames():
        logging.error("get_avg_rating_by_feature_from_project_id::Project not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"id": project_id, "Error": "Project not found"},
        )
    feature_urls = yaml_repo.getFeatureUrlsFromProjectName(project.name)
    for url in feature_urls:
        output.append(
            {"url": url, "rating": sqlite_repo.get_feature_avg_rating(project.id, url)}
        )
    return output

@inject
async def get_rules_from_project_id(
    project_id: int,
    sqlite_repo: SQLiteRepository = Depends(Provide[Container.sqlite_repo]),
    yaml_repo: YamlRulesRepository = Depends(Provide[Container.rules_config]),
) -> List[Rule]:
    """
    Returns the rules for a project with the given ID.

    Args:
        id (int): the ID of the project to retrieve rules for
        sqlite_repo (SQLiteRepository): the SQLite repository to use for accessing project information
        yaml_repo (YamlRulesRepository): the YAML repository to use for accessing rule information

    Returns:
        Union[List, dict]: a list of rules for the project, or an error dictionary if the project is not found
    """
    project = await sqlite_repo.get_project_by_id(project_id)

    if not project or project.name not in yaml_repo.getProjectNames():
        logging.error("get_rules_from_project_id::Project not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"id": project_id, "Error": "Project not found"},
        )

    return yaml_repo.getRulesFromProjectName(project.name)

@inject
async def get_avg_project_rating_from_id(
    project_id: int,
    sqlite_repo: SQLiteRepository = Depends(Provide[Container.sqlite_repo]),
    yaml_repo: YamlRulesRepository = Depends(Provide[Container.rules_config]),
) -> float:
    """
    Retrieve the average rating of a project with the given id.

    Args:
        id (int): The id of the project to retrieve the rating for.
        sqlite_repo (SQLiteRepository, optional): The SQLiteRepository instance to use for database access.
            Defaults to Depends(Provide[Container.sqlite_repo]).
        yaml_repo (YamlRulesRepository, optional): The YamlRulesRepository instance to use for rules configuration.
            Defaults to Depends(Provide[Container.rules_config]).

    Returns:
        float: the average rating, or an error message if the project
        was not found or if its name is not included in the list of project names in the YamlRulesRepository.
    """

    project = await sqlite_repo.get_project_by_id(project_id)
    if not project or project.name not in yaml_repo.getProjectNames():
        logging.error("get_avg_project_rating_from_id::Project not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"id": project_id, "Error": "Project not found"},
        )
    rating = sqlite_repo.get_project_avg_rating(project_id)
    return rating
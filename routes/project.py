

from fastapi import APIRouter, Depends

from dependency_injector.wiring import Provide, inject
from repository.sqlite_repository import SQLiteRepository
from repository.yaml_rule_repository import YamlRulesRepository
from utils.container import Container

router = APIRouter()

@router.get("/project/{id}/rating", response_model=dict)
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
        return {"id": id, "Error": "Project not found"}
    rating = sqlite_repo.get_project_avg_rating(id)
    return {
        "id": id,
        "rating": rating
    }



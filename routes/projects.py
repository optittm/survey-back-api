from typing import List
from fastapi import APIRouter, Security

from models.rule import Rule
from models.security import ScopeEnum
from survey_logic import projects as logic
from routes.middlewares.security import check_jwt

router = APIRouter()


@router.get(
    "/projects",
    dependencies=[Security(check_jwt, scopes=[ScopeEnum.DATA.value])],
    response_model=List[dict],
)
async def get_projects() -> List[dict]:
    return await logic.get_all_projects()


@router.get(
    "/projects/{id}/avg_feature_rating",
    dependencies=[Security(check_jwt, scopes=[ScopeEnum.DATA.value])],
    response_model=List[dict],
)
async def get_projects_feature_rating(id: int) -> List[dict]:
    return await logic.get_avg_rating_by_feature_from_project_id(id)


@router.get(
    "/projects/{id}/rules",
    dependencies=[Security(check_jwt, scopes=[ScopeEnum.DATA.value])],
    response_model=List[Rule],
)
async def get_projects_rules(id: int) -> List[Rule]:
    return await logic.get_rules_from_project_id(id)


@router.get(
    "/projects/{id}/avg_rating",
    dependencies=[Security(check_jwt, scopes=[ScopeEnum.DATA.value])],
    response_model=float,
)
async def get_project_rating(id: int) -> float:
    return await logic.get_avg_project_rating_from_id(id)

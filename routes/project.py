

from fastapi import APIRouter, Depends

from dependency_injector.wiring import Provide, inject
from repository.sqlite_repository import SQLiteRepository
from utils.container import Container

router = APIRouter()

@router.get("/project/{id}/rating", response_model=dict)
@inject
async def get_project_rating(
    id: int,
    sqlite_repo: SQLiteRepository = Depends(Provide[Container.sqlite_repo])
) -> dict:  
    rating = sqlite_repo.get_project_avg_rating(id)
    return {
        "id": id,
        "rating": rating
    }



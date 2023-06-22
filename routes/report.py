from fastapi import APIRouter
from typing import Optional
from fastapi import APIRouter, Security
from fastapi.responses import HTMLResponse

from survey_logic import report
from models.security import ScopeEnum
from routes.middlewares.security import check_jwt

router = APIRouter()

@router.get(
    "/survey-report",
    dependencies=[Security(check_jwt, scopes=[ScopeEnum.DATA.value])],
    response_class=HTMLResponse,
)
async def init_project_report() -> str:
    return await report.generate_project_report()


@router.get(
    "/survey-report/project/{id}",
    dependencies=[Security(check_jwt, scopes=[ScopeEnum.DATA.value])],
    response_class=HTMLResponse,
)
async def init_detail_project_report(
    id: int, 
    timerange: Optional[str] = "week", 
    timestamp_start: Optional[str] = None, 
    timestamp_end: Optional[str] = None,
) -> str:
    return await report.generate_detailed_report_from_project_id(
        id, timerange, timestamp_start, timestamp_end
    )


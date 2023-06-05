from typing import Optional
from fastapi import APIRouter, Security
from fastapi.responses import HTMLResponse
from models.security import ScopeEnum
from repository.html_repository import HTMLRepository

import jinja2

from routes.middlewares.security import check_jwt

router = APIRouter()


templates = jinja2.Template("templates")


@router.get(
    "/survey-report",
    dependencies=[Security(check_jwt, scopes=[ScopeEnum.DATA.value])],
    response_class=HTMLResponse,
)
async def init_report() -> str:
    html_repository = HTMLRepository(reportFile="surveyReport.html")
    return html_repository.generate_report()


@router.get(
    "/survey-report/project/{id}",
    dependencies=[Security(check_jwt, scopes=[ScopeEnum.DATA.value])],
    response_class=HTMLResponse,
)
async def init_detail_project_report(
    id: str, timestamp_start: Optional[str] = None, timestamp_end: Optional[str] = None
) -> str:
    html_repository = HTMLRepository(reportFile="surveyProjectDetailReport.html")
    return html_repository.generate_detail_project_report(
        id, timestamp_start, timestamp_end
    )

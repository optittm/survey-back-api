from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from repository.html_repository import HTMLRepository

import jinja2

router = APIRouter()


templates = jinja2.Template("templates")


@router.get("/survey-report", response_class=HTMLResponse)
async def init_report() -> str:
    html_repository = HTMLRepository()
    return html_repository.generate_report()

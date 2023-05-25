from fastapi import APIRouter, Depends

from dependency_injector.wiring import Provide, inject
from fastapi.responses import HTMLResponse
from repository.html_repository import HTMLRepository

from utils.container import Container

import jinja2

from repository.sqlite_repository import SQLiteRepository
from repository.yaml_rule_repository import YamlRulesRepository

router = APIRouter()


templates = jinja2.Template("templates")


@router.get("/survey-report", response_class=HTMLResponse)
@inject
async def init_report(
    sqlite_repo: SQLiteRepository = Depends(Provide[Container.sqlite_repo]),
    rulesYamlConfig: YamlRulesRepository = Depends(Provide[Container.rules_config]),
) -> str:
    html_repository = HTMLRepository()

    nameProjects = rulesYamlConfig.getProjectNames()

    for project_name in nameProjects:
        project = await sqlite_repo.get_project_by_name(project_name)
        project_average_rating = sqlite_repo.get_project_avg_rating(project.id)
        comments_number = sqlite_repo.get_number_of_comment(project.id)
        display_modal_number = sqlite_repo.get_number_of_display(project.id)
    
    return html_repository.generate_report(nameProjects)

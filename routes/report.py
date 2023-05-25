from fastapi import APIRouter, Depends

from dependency_injector.wiring import Provide, inject
from typing import Optional
from fastapi import APIRouter
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
    html_repository = HTMLRepository(reportFile="surveyReport.html")

    projects = []

    for project_name in rulesYamlConfig.getProjectNames():
        project = await sqlite_repo.get_project_by_name(project_name)
        average_rating = sqlite_repo.get_project_avg_rating(project.id)
        comments_number = sqlite_repo.get_number_of_comment(project.id)
        display_modal_number = sqlite_repo.get_number_of_display(project.id)
        active_rules = [
            rule
            for rule in rulesYamlConfig.getRulesFromProjectName(project_name)
            if rule.is_active == True
        ]

        projects.append(
            {
                "name": project_name,
                "average_rating": average_rating,
                "comments_number": comments_number,
                "display_modal_number": display_modal_number,
                "active_rules_number": len(active_rules),
            }
        )

    return html_repository.generate_report(projects)


@router.get("/survey-report/project/{id}", response_class=HTMLResponse)
async def init_detail_project_report(
    id: str, timestamp_start: Optional[str] = None, timestamp_end: Optional[str] = None
) -> str:
    html_repository = HTMLRepository(reportFile="surveyProjectDetailReport.html")
    return html_repository.generate_detail_project_report(
        id, timestamp_start, timestamp_end
    )

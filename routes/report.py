from typing import Optional
from fastapi import APIRouter, Security
from fastapi.responses import HTMLResponse
from models.security import ScopeEnum
from repository.html_repository import HTMLRepository

import jinja2
import plotly.express as px
import pandas as pd
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from repository.html_repository import HTMLRepository
from repository.sqlite_repository import SQLiteRepository
from repository.yaml_rule_repository import YamlRulesRepository

from utils.container import Container
from dependency_injector.wiring import inject, Provide

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
@inject
async def init_detail_project_report(
    id: str, 
    timerange: Optional[str] = "week", 
    timestamp_start: Optional[str] = None, 
    timestamp_end: Optional[str] = None,
    sqlite_repo: SQLiteRepository = Depends(Provide[Container.sqlite_repo]),
    yaml_repo: YamlRulesRepository = Depends(Provide[Container.rules_config])
) -> str:
    """
    Generates the detailed project report for the specified project ID.

    Args:
        id (str): The ID of the project.
        timerange (str, optional): The time range for the report. Defaults to "week".
        timestamp_start (str, optional): The start timestamp for filtering the rates. Defaults to None.
        timestamp_end (str, optional): The end timestamp for filtering the rates. Defaults to None.
        sqlite_repo (SQLiteRepository, optional): The SQLite repository. Defaults to Depends(Provide[Container.sqlite_repo]).
        yaml_repo (YamlRulesRepository, optional): The YAML rules repository. Defaults to Depends(Provide[Container.rules_config]).

    Returns:
        str: The generated detailed project report in HTML format.

    """

    html_repository = HTMLRepository(reportFile="surveyProjectDetailReport.html")
    project = await sqlite_repo.get_project_by_id(id)
    project_name = project.name
    feature_urls = yaml_repo.getFeatureUrlsFromProjectName(project_name)
    feature_rates = {}
    
    for feature_url in feature_urls:
        rates = await sqlite_repo.get_rates_from_feature(feature_url)
        feature_rates[feature_url] = rates
    filtered_rates = await sqlite_repo.filter_rates_by_timerange(feature_rates, timerange, timestamp_start, timestamp_end)

    graphs = []
    date_timestamp_start = []
    date_timestamp_end = []

    for feature_url, rates in filtered_rates.items():
        if feature_url == 'date_timestamp_start':
            date_timestamp_start = rates
            continue
        elif feature_url == 'date_timestamp_end':
            date_timestamp_end = rates
            continue

        x = [rate["date_timestamp"] for rate in rates if "date_timestamp" in rate]
        y = [rate["rate"] for rate in rates]
        df = pd.DataFrame({'timestamp': x, 'rates': y})
        fig = px.box(df, x='timestamp', y='rates', labels={'timestamp': 'Timestamp','rates': 'Rates'})
        fig.update_layout(yaxis=dict(range=[0, 6]))

        fig_html = fig.to_html(full_html=False, include_plotlyjs=False)
        graph_data = {
            "feature_url": feature_url,
            "comment_count": len(rates),
            "figure_html": fig_html
        }
        graphs.append(graph_data)

    return html_repository.generate_detail_project_report(
        id, timerange, date_timestamp_start, date_timestamp_end, graphs
    )


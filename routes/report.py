from typing import Optional
import jinja2
import plotly.graph_objects as go
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from repository.html_repository import HTMLRepository
from repository.sqlite_repository import SQLiteRepository
from repository.yaml_rule_repository import YamlRulesRepository

from utils.container import Container
from dependency_injector.wiring import inject, Provide

router = APIRouter()

templates = jinja2.Template("templates")

@router.get("/survey-report", response_class=HTMLResponse)
async def init_report() -> str:
    html_repository = HTMLRepository(reportFile="surveyReport.html")
    return html_repository.generate_report()

@router.get("/survey-report/project/{id}", response_class=HTMLResponse)
@inject
async def init_detail_project_report(
    id: str, 
    timestamp_start: Optional[str] = None, 
    timestamp_end: Optional[str] = None,
    sqlite_repo: SQLiteRepository = Depends(Provide[Container.sqlite_repo]),
    yaml_repo: YamlRulesRepository = Depends(Provide[Container.rules_config])
) -> str:
    
    html_repository = HTMLRepository(reportFile="surveyProjectDetailReport.html")
    
    project = await sqlite_repo.get_project_by_id(id)
    project_name = project.name
    feature_urls = yaml_repo.getFeatureUrlsFromProjectName(project_name)
    feature_rates = {}

    for feature_url in feature_urls:
        rates = await sqlite_repo.get_rates_from_feature(feature_url)
        feature_rates[feature_url] = rates

    graphs = []
    for feature_url, rates in feature_rates.items():
        x = [rate["timestamp"] for rate in rates]
        y = [rate["rate"] for rate in rates]
        
        fig = go.Figure(data=go.Scatter(x=x, y=y, mode='markers', name=feature_url))

        fig.update_layout(yaxis=dict(range=[0, 6]))

        fig_html = fig.to_html(full_html=False, include_plotlyjs=False)
        graph_data = {
            "feature_url": feature_url,
            "comment_count": len(rates),
            "figure_html": fig_html
        }
        graphs.append(graph_data)

    return html_repository.generate_detail_project_report(
        id, timestamp_start, timestamp_end, graphs
    )
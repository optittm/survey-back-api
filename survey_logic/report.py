from fastapi import Depends
from dependency_injector.wiring import Provide, inject
from typing import Optional
import plotly.express as px
import pandas as pd

from utils.html_report import HTMLReport
from repository.sqlite_repository import SQLiteRepository
from repository.yaml_rule_repository import YamlRulesRepository
from utils.container import Container

import numpy as np

@inject
async def generate_project_report(
    sqlite_repo: SQLiteRepository = Depends(Provide[Container.sqlite_repo]),
    rulesYamlConfig: YamlRulesRepository = Depends(Provide[Container.rules_config]),
) -> str:
    """
    Generates a report for all projects with different statistics

    Returns:
        str: The report in HTML format
    """
    html_repository = HTMLReport(reportFile="surveyReport.html")

    projects = []

    for project_name in rulesYamlConfig.getProjectNames():
        project = await sqlite_repo.get_project_by_name(project_name)
        average_rating = sqlite_repo.get_project_avg_rating(project.id)
        comments_number = sqlite_repo.get_number_of_comment(project.id)
        display_modal_number = sqlite_repo.get_number_of_display(project.id)
        feature_urls = await sqlite_repo.get_features_urls_by_project_name(project_name)
        active_rules = [
            rule
            for rule in rulesYamlConfig.getRulesFromProjectName(project_name)
            if rule.is_active
        ]
        feature_data = []
        for feature_url in feature_urls:
            feature_avg_rating = sqlite_repo.get_feature_avg_rating(project.id, feature_url)
            feature_avg_rating= round(feature_avg_rating, 1)
            feature_data.append({
                'feature_url': feature_url,
                'feature_avg_rating': feature_avg_rating
            })

        projects.append(
            {
                "name": project_name,
                "feature_data": feature_data,
                "average_rating": round(average_rating, 1),
                "comments_number": comments_number,
                "display_modal_number": display_modal_number,
                "active_rules_number": len(active_rules),
            }
        )

    return html_repository.generate_report(projects)

#Ponderates an array of notes by score and date
#Curently the date is registered as DD/MM/YYYY so the granularity is daily
#This function has been added to improve the graph design

def ponderate(notes)->[] : 
    if len(notes) <=0 :
        return []
    notes_pond=[]
    notes=sorted(notes,key=lambda x: (x['note'], x['day']))
    for note in notes : 
        added = 0
        i=0
        for note_p in notes_pond :
            
            if note_p["day"] == note["day"] and note_p["note"] == note["note"]:
                count=note_p["count"] +1
                del notes_pond[i]
                notes_pond.append({
                    'note' : note["note"],
                    'count' : count,
                    'day' : note["day"],
                })
                added = 1
            i +=1
        if added == 0 : 
            notes_pond.append({
                'note' : note["note"],
                'count' : note["count"],
                'day' : note["day"],
            })
    return notes_pond

@inject
async def generate_detailed_report_from_project_id(
    project_id: int,
    timerange: Optional[str] = "week", 
    timestamp_start: Optional[str] = None, 
    timestamp_end: Optional[str] = None,
    sqlite_repo: SQLiteRepository = Depends(Provide[Container.sqlite_repo]),
    yaml_repo: YamlRulesRepository = Depends(Provide[Container.rules_config]),
) -> str:
    """
    Generates the detailed project report for the specified project ID.

    Args:
        id (int): The ID of the project.
        timerange (str, optional): The time range for the report. Defaults to "week".
        timestamp_start (str, optional): The start timestamp for filtering the rates. Defaults to None.
        timestamp_end (str, optional): The end timestamp for filtering the rates. Defaults to None.
        sqlite_repo (SQLiteRepository, optional): The SQLite repository. Defaults to Depends(Provide[Container.sqlite_repo]).
        yaml_repo (YamlRulesRepository, optional): The YAML rules repository. Defaults to Depends(Provide[Container.rules_config]).

    Returns:
        str: The generated detailed project report in HTML format.

    """

    html_repository = HTMLReport(reportFile="surveyProjectDetailReport.html")
    project = await sqlite_repo.get_project_by_id(project_id)
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
    notes_sec = []

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
            "figure_html": fig_html,
        }
        graphs.append(graph_data)
        notes_sec=[({
            'note': str(rate["rate"]),
            'count': 1,
            'day':str(rate["date_timestamp"]),
            }) for rate in rates]
        notes_sec_pond=[]
        #If empty the graph lib shows an error about x (first argument) that receive a bad format []
        if(len(notes_sec)>0) :
            notes_sec_pond=ponderate(notes_sec)
            fig_sec = px.bar(
                notes_sec_pond, 
                x="day", y="count", 
                color="note", 
                title="Totals notes", 
                color_discrete_map={
                    "1": "red", 
                    "2": "orange", 
                    "3": "yellow", 
                    "4": "lightGreen", 
                    "5": "green",
            })
            fig_html_2 = fig_sec.to_html(full_html=False, include_plotlyjs=False)
            graph_data_2 = {
                "feature_url": feature_url,
                "comment_count": len(notes_sec),
                "figure_html": fig_html_2,
            }
            graphs.append(graph_data_2)

    return html_repository.generate_detail_project_report(
        project_id, timerange, date_timestamp_start, date_timestamp_end, graphs
    )
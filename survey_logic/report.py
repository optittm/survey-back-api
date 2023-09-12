from fastapi import Depends
from dependency_injector.wiring import Provide, inject
from typing import Optional
import plotly.express as px
import pandas as pd
from survey_logic.comments import get_comments

from utils.html_report import HTMLReport
from repository.sqlite_repository import SQLiteRepository
from repository.yaml_rule_repository import YamlRulesRepository
from utils.container import Container

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

def ponderate_generated(list,x_name,y_name,count_name, color_name)->[] : 
    if len(list) <=0 :
        return []
    list_pond=[]
    list=sorted(list,key=lambda x: (x[y_name], x[x_name]))
    for val in list : 
        added = 0
        i=0
        for val_p in list_pond :
            
            if val_p[x_name] == val[x_name] and val_p[y_name] == val[y_name] and val_p[color_name] == val[color_name]:
                count=val_p[count_name] +1
                del list_pond[i]
                list_pond.append({
                y_name : val[y_name],
                    count_name : count,
                    x_name : val[x_name],
                    color_name : val[color_name]
            })
                added = 1
                break
            i +=1
        if added == 0 : 
            list_pond.append({
                y_name : val[y_name],
                    count_name : val[count_name],
                    x_name : val[x_name],
                    color_name : val[color_name]
            })
    return list_pond

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
    comments={}
    
    for feature_url in feature_urls:
        rates = await sqlite_repo.get_rates_from_feature(feature_url)
        feature_rates[feature_url] = rates
        comments[feature_url] = await get_comments(project_name, feature_url)
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

    # for feature_url in feature_url:
    for feature,comment_list in comments.items() : 
        comments = []
        for comment in comment_list : 
            #rating (1-5), sentiment: POSITIVE/NEGATIVE, sentiment_score 0.99234253245
            # print(comment.comment)
            if(comment.sentiment_score) : 
            
                comments.append({
                    'rating' : comment.rating,
                    'sentiment_score' : comment.sentiment_score,
                    'color' : comment.sentiment,
                    'count' : 1
                })
        if(len(comments)>0): 
            fig_1 = px.scatter(comments, y="rating", x="sentiment_score",size = "count", color="color", color_discrete_map={
                "NEGATIVE": "red", "POSITIVE": "green"
            })
            # fig_1.update_layout(yaxis=dict(range=[0, 6]))

            fig_html_1 = fig_1.to_html(full_html=False, include_plotlyjs=False)
            graph_data_1 = {
                "feature_url": feature,
                "comment_count": len(comments),
                "figure_html": fig_html_1
            }
            graphs.append(graph_data_1)
            print(comments)
            comments_pond = ponderate_generated(comments,'sentiment_score', 'rating','count',"color" )
            print(comments_pond)
            # print(comments_pound[0]["sentiment_score"])
            fig = px.scatter(comments_pond, y="rating", x="sentiment_score",size = "count", color="color", color_discrete_map={
                "NEGATIVE": "red", "POSITIVE": "green"
            })
            fig.update_layout(yaxis=dict(range=[0, 6]))

            fig_html = fig.to_html(full_html=False, include_plotlyjs=False)
            graph_data = {
                "feature_url": feature,
                "comment_count": len(comments_pond),
                "figure_html": fig_html
            }
            graphs.append(graph_data)
    
    return html_repository.generate_detail_project_report(
        project_id, timerange, date_timestamp_start, date_timestamp_end, graphs
    )
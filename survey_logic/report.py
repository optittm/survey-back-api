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

#Ponderates an array of dict based on 4 parameters add one to count if the three others are equals
#Possibly make some optional like the color for other array to be ponderate

def generic_ponderate(list,x_name,y_name,count_name, color_name, optional : Optional[str]=None )->[] : 
    if len(list) <=0 :
        return []
    list_pond=[]
    list = sorted(list,key=lambda x: (x[y_name], x[x_name]))
    for val in list : 
        added = 0
        i=0
        for val_p in list_pond :
            
            if (val_p[x_name] == val[x_name] and 
                val_p[y_name] == val[y_name] and 
                val_p[color_name] == val[color_name] ):
                count=val_p[count_name] +1
                del list_pond[i]
                if(optional) :
                    list_pond.append({
                        y_name : val[y_name],
                        count_name : count,
                        x_name : val[x_name],
                        color_name : val[color_name],
                        optional : val[optional],
                    })
                else : 
                    list_pond.append({
                        y_name : val[y_name],
                        count_name : count,
                        x_name : val[x_name],
                        color_name : val[color_name],
                    })
                added = 1
                break
            i +=1
        if added == 0 : 
            if(optional) :
                list_pond.append({
                    y_name : val[y_name],
                    count_name : val[count_name],
                    x_name : val[x_name],
                    color_name : val[color_name],
                    optional : val[optional],
                })
            else :
                list_pond.append({
                    y_name : val[y_name],
                    count_name : val[count_name],
                    x_name : val[x_name],
                    color_name : val[color_name],
                })
    return list_pond
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
    comments={}
    for feature_url in feature_urls:
        rates = await sqlite_repo.get_rates_from_feature(feature_url)
        feature_rates[feature_url] = rates
        comments[feature_url] = await get_comments(project_name, feature_url,timestamp_start= timestamp_start, timestamp_end = timestamp_end)

    filtered_rates = await sqlite_repo.filter_rates_by_timerange(feature_rates, timerange, timestamp_start, timestamp_end)
    graphs = []
    date_timestamp_start = []
    date_timestamp_end = []
    notes_sec = []

    for feature,comment_list in comments.items() : 
        comments = []
        for comment in comment_list : 
            if(comment.sentiment_score) : 
                comments.append({
                    'rating' : comment.rating,
                    'sentiment_score' : comment.sentiment_score,
                    'color' : comment.sentiment,
                    'count' : 1,
                    'date' : str((comment.timestamp).split("T",1)[0]),
                })
        if(len(comments)>0): 
            comments_pond = generic_ponderate(comments,'sentiment_score', 'rating','count','color','date' )
            comment_fig = px.scatter(
                comments_pond, 
                y="rating", 
                x="sentiment_score",
                size = "count", 
                color="color", 
                color_discrete_map={
                    "NEGATIVE": "red", 
                    "POSITIVE": "green",
            })
            total_comments = sum([comment['count'] for comment in comments_pond])
            comment_fig.update_layout(yaxis = dict(range=[0, 6]))
            comment_fig_html = comment_fig.to_html(full_html=False, include_plotlyjs=False)
            graph_data_comments = {
                "feature_url": feature,
                "comment_count": total_comments,
                "figure_html": comment_fig_html,
            }
            graphs.append(graph_data_comments)

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

        fig_html_comments = fig.to_html(full_html=False, include_plotlyjs=False)
        graph_data_comments = {
            "feature_url": feature_url,
            "comment_count": len(rates),
            "figure_html": fig_html_comments,
        }
        graphs.append(graph_data_comments)
        notes_sec=[({
            'note': str(rate["rate"]),
            'count': 1,
            'day':str(rate["date_timestamp"]),
            'color': str(rate["rate"]),
            }) for rate in rates]
        notes_sec_pond=[]
        #If empty the graph lib shows an error about x (first argument) that receive a bad format []
        if(len(notes_sec)>0) :
            notes_sec_pond=generic_ponderate(notes_sec,'note','day','count','color')
            notes_fig = px.bar(
                notes_sec_pond, 
                x="day", 
                y="count", 
                color="color", 
                title="Totals notes", 
                color_discrete_map={
                    "1": "red", 
                    "2": "orange", 
                    "3": "yellow", 
                    "4": "lightGreen", 
                    "5": "green",
            }   )
            total_notes = sum([note['count'] for note in notes_sec_pond])
            #For future use
            moyenne_notes = sum([note['count'] * int(note['note']) for note in notes_sec_pond ]) / total_notes
            median_notes = np.median(np.sort([int(note['note']) for note in notes_sec_pond for _ in range(note['count'])]))

            notes_fig_html = notes_fig.to_html(full_html=False, include_plotlyjs=False)
            graph_data_notes = {
                "feature_url": feature_url,
                "comment_count": total_notes,
                "figure_html": notes_fig_html,
            }
            graphs.append(graph_data_notes)
    return html_repository.generate_detail_project_report(
        project_id, timerange, date_timestamp_start, date_timestamp_end, graphs
    )
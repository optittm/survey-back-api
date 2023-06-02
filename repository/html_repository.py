import logging
import os
from typing import List
import jinja2
import plotly.graph_objects as go

class HTMLRepository:
    """
    Generate an HTML report
    """

    def __init__(self, reportFile: str) -> None:
        # Load HTML template
        self.template_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "../templates/"
        )

        # Get the template
        self.template_loader = jinja2.FileSystemLoader(searchpath=self.template_path)
        self.template_env = jinja2.Environment(loader=self.template_loader)
        self.template = self.template_env.get_template(reportFile)

    def generate_report(self) -> str:
        logging.info("Generate HTML report")

        data = {
            "project": "TestName",
        }

        # Render the template and return Report
        html_report = self.template.render(data)
        return html_report

    def generate_detail_project_report(
        self, 
        id: str,
        timerange: str= "week",
        timestamp_start: str = None, 
        timestamp_end: str = None,
        graphs: List[go.Figure] = None,
    ) -> str:
        logging.info("Generate Detail Project Report")
        
        data = {
            "project": {"id": id},
            "timestamp_start": timestamp_start,
            "timestamp_end": timestamp_end,
            "graphs": graphs,
            "timerange":timerange,
        }

        # Render the template and return Report
        html_report = self.template.render(data)
        return html_report

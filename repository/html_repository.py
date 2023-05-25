import logging
import os
import jinja2


class HTMLRepository:
    """
    Generate an HTML report
    """

    def generate_report(self, projects) -> str:
        logging.info("Generate HTML report")

        # Load HTML template
        template_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "../templates/"
        )

        data = {
            "project": "TestName",
        }

        # Render the template and save the output
        template_loader = jinja2.FileSystemLoader(searchpath=template_path)
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template("surveyReport.html")
        output_text = template.render(data)

        return output_text

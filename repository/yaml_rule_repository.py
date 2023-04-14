from typing import List
import yaml
from schema import Schema, SchemaError, Optional
from yaml.loader import SafeLoader
from models.rule import Rule


class YamlRulesRepository:
    _RULES_CONFIG_FILE = "rules.yaml"

    _RULES_CONFIG_SCHEMA = {
        Optional("get_comments_allowed_origins"): str,
        Optional("front_allowed_origins"): str,
        "projects": {
            str: {
                "rules": [
                    {
                        "feature_url": str,
                        "ratio": float,
                        "delay_before_reanswer": int,
                        "delay_to_answer": int,
                        "is_active": bool,
                    }
                ]
            }
        },
    }

    @staticmethod
    def _getRulesConfig(file_name: str = _RULES_CONFIG_FILE):
        """
        Loads the rule configuration data from the specified YAML file and validates it against the specified schema using the Schema library.

        Args:
            file_name (str): The name of the YAML file to load.

        Returns:
            dict: A dictionary containing the rule configuration data if the file exists and is valid against the schema.
            None if the file does not exist or if it is not valid against the schema.
        """
        try:
            with open(file_name) as f:
                data = yaml.load(f, Loader=SafeLoader)
                schema = Schema(
                    YamlRulesRepository._RULES_CONFIG_SCHEMA, ignore_extra_keys=True
                )
                schema.validate(data)
                return data
        except FileNotFoundError:
            print(f"File {file_name} not found")
            return None
        except SchemaError as exc:
            print(f"Error while validating the file {file_name}: {exc}")
            return None
        except yaml.YAMLError as exc:
            print(f"Error while parsing the file {file_name}: {exc}")
            return None

    @staticmethod
    def getRuleFromFeature(feature_url: str):
        """
        Returns a Rule object corresponding to the specified feature URL, or None if the feature does not exist in the rule configuration.

        Args:
        feature_url (str): The URL of the feature for which to retrieve the rule.

        Returns:
        Rule: A Rule object containing the information for the corresponding rule, if it exists.
            None if the feature does not exist in the rule configuration.
        """
        data = YamlRulesRepository._getRulesConfig(
            YamlRulesRepository._RULES_CONFIG_FILE
        )
        if data:
            for project_name, project_data in data["projects"].items():
                for rule in project_data["rules"]:
                    if rule["feature_url"] == feature_url:
                        return Rule(
                            rule["feature_url"],
                            rule["ratio"],
                            rule["delay_before_reanswer"],
                            rule["delay_to_answer"],
                            rule["is_active"],
                        )
        return None

    @staticmethod
    def getProjectNameFromFeature(feature_url: str):
        """
        Returns the name of the project to which the specified feature URL belongs, or None if the feature does not exist in the rule configuration.

        Args:
        feature_url (str): The URL of the feature for which to retrieve the project name.

        Returns:
        str: The name of the project to which the feature belongs, if it exists.
            None if the feature does not exist in the rule configuration.
        """
        data = YamlRulesRepository._getRulesConfig(
            YamlRulesRepository._RULES_CONFIG_FILE
        )
        if data:
            for project_name, project_data in data["projects"].items():
                for rule in project_data["rules"]:
                    if rule["feature_url"] == feature_url:
                        return project_name
        return None

    @staticmethod
    def getProjectNames() -> List[str]:
        """
        Returns the names of the projects listed in the YAML config file
        """
        data = YamlRulesRepository._getRulesConfig(
            YamlRulesRepository._RULES_CONFIG_FILE
        )
        if data:
            return data["projects"].keys()
        return None

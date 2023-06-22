from dependency_injector import containers, providers

from repository.yaml_rule_repository import YamlRulesRepository
from repository.sqlite_repository import SQLiteRepository
from utils.nlp import SentimentAnalysis, NlpPreprocess


class Container(containers.DeclarativeContainer):
    # Wiring the modules which need dependency injection
    # If you need to use Provide in a file other than main.py, add it to the list of modules here
    wiring_config = containers.WiringConfiguration(
        modules=[
            "routes.comments",
            "routes.rules",
            "routes.report",
            "routes.projects",
            "utils.formatter",
            "routes.middlewares.security",
            "routes.security",
        ]
    )

    config = providers.Configuration()

    rules_config = providers.Singleton(YamlRulesRepository)
    sqlite_repo = providers.Singleton(SQLiteRepository, config=config)

    sentiment_analysis = providers.Singleton(SentimentAnalysis, config=config)
    nlp_preprocess = providers.Singleton(NlpPreprocess, config=config)

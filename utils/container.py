from dependency_injector import containers, providers

from repository.yaml_rule_repository import YamlRulesRepository
from repository.sqlite_repository import SQLiteRepository
from repository.html_repository import HTMLRepository


class Container(containers.DeclarativeContainer):
    # Wiring the modules which need dependency injection
    # If you need to use Provide in a file other than main.py, add it to the list of modules here
    wiring_config = containers.WiringConfiguration(
        modules=["routes.comments", "routes.rules", "routes.report", "utils.formatter"]
    )

    config = providers.Configuration()

    rules_config = providers.Singleton(YamlRulesRepository)
    sqlite_repo = providers.Singleton(SQLiteRepository)
    html_config = providers.Singleton(HTMLRepository)

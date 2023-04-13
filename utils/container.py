from dependency_injector import containers, providers

from repository.yaml_rule_repository import YamlRulesRepository
from repository.sqlite_repository import SQLiteRepository

class Container(containers.DeclarativeContainer):

    # Wiring the modules which need dependency injection
    # If you need to use Provide in a file other than main.py, add it to the list of modules here
    wiring_config = containers.WiringConfiguration(modules=["routes.comments","utils.formatter"])

    config = providers.Configuration()

    rules_config = providers.Object(YamlRulesRepository)
    sqlite_repo = providers.Singleton(SQLiteRepository)
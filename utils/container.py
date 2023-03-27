from dependency_injector import containers, providers
from sqlalchemy.orm import sessionmaker

from repository.FeatureConfig import FeatureConfig
from repository.DBrepository import CommentRepository

class Container(containers.DeclarativeContainer):

    # Wiring the modules which need dependency injection
    # If you need to use Provide in a file other than main.py, add it to the list of modules here
    wiring_config = containers.WiringConfiguration(modules=["routes.comments"])

    config = providers.Configuration()

    features_config = providers.Factory(FeatureConfig)
    db_manager = providers.Singleton(CommentRepository)
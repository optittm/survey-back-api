from dependency_injector import containers, providers
from sqlalchemy.orm import sessionmaker

from repository.FeatureConfig import FeatureConfig

class Container(containers.DeclarativeContainer):

    # Wiring the modules which need dependency injection
    # If you need to use Provide in a file other than main.py, add it to the list of modules here
    # wiring_config = containers.WiringConfiguration(modules=["routes.comments"])

    config = providers.Configuration()

    Session = sessionmaker()
    db_session = providers.Singleton(Session)

    features_config = providers.Factory(FeatureConfig)
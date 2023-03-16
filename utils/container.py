from dependency_injector import containers, providers
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker

from repository.FeatureConfig import FeatureConfig

class Container(containers.DeclarativeContainer):
    load_dotenv()

    config = providers.Configuration()

    Session = sessionmaker()
    db_session = providers.Singleton(Session)

    features_config = providers.Factory(FeatureConfig)
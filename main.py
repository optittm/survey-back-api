import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dependency_injector.wiring import Provide, inject
from models.display import Display
import uvicorn
from sqlalchemy.exc import ArgumentError
from pydbantic import Database
import logging

from models.comment import Comment
from models.project import Project, ProjectEncryption
from routes.comments import router as comment_router
from routes.rules import router as rule_router
from routes.project import router as project_router
from routes.report import router as report_router
from utils.container import Container
from utils.formatter import str_to_bool


@inject
def init_fastapi(config=Provide[Container.config], prefix="/api/v1") -> FastAPI:
    logging.info("Init FastAPI app")
    # Creates the FastAPI instance inside the function to be able to use the config provider
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config["cors_allow_origins"].split(","),
        allow_credentials=config["cors_allow_credentials"],
        allow_methods=config["cors_allow_methods"].split(","),
        allow_headers=config["cors_allow_headers"].split(","),
    )

    app.include_router(comment_router, prefix=prefix)
    app.include_router(rule_router, prefix=prefix)
    app.include_router(project_router, prefix=prefix)
    app.include_router(report_router, prefix=prefix)

    return app


@inject
async def main(config=Provide[Container.config]):
    await init_db()
    # Running the uvicorn server in the function to be able to use the config provider
    config = uvicorn.Config(
        "main:app",
        host=config["survey_api_host"],
        reload=config["debug_mode"],
        port=config["survey_api_port"],
        log_level=config["log_level"].lower(),
    )
    # Running the server in the existing async loop
    # https://www.uvicorn.org/#config-and-server-instances
    server = uvicorn.Server(config)
    logging.info("Starting uvicorn server")
    await server.serve()


@inject
async def init_db(
    config=Provide[Container.config],
    rules_config=Provide[Container.rules_config],
    sqlite_repo=Provide[Container.sqlite_repo],
):
    try:
        db = await Database.create(
            config["survey_db"], tables=[Project, Comment, ProjectEncryption, Display]
        )
        logging.info("Database ready")
    except ArgumentError as e:
        logging.error("Error initialising the database")
        raise Exception(f"Error from sqlalchemy : {str(e)}")

    project_names = rules_config.getProjectNames()
    for project_name in project_names:
        await sqlite_repo.create_project(Project(name=project_name))


@inject
def config_logging(config=Provide[Container.config]):
    logging.basicConfig(level=config["log_level"])


load_dotenv()
container = Container()
# Loading .env variables into the config provider
container.config.survey_api_host.from_env(
    "SURVEY_API_HOST", required=True, default="localhost"
)
container.config.survey_api_port.from_env(
    "SURVEY_API_PORT", required=True, as_=int, default=8000
)
# from_env default only applies when the statement VAR= is compeltely absent from the env file
# Writing VAR= with no following value returns an empty string,
# thus the use of a lambda expression to apply the default in this case and avoid an error
container.config.survey_db.from_env(
    "SURVEY_DB",
    required=True,
    as_=lambda x: x if x != "" else "sqlite:///data/survey.sqlite3",
    default="sqlite:///data/survey.sqlite3",
)
container.config.use_fingerprint.from_env(
    "USE_FINGERPRINT",
    required=True,
    as_=lambda x: str_to_bool(x) if x != "" else False,
    default="False",
)
container.config.cors_allow_origins.from_env("CORS_ALLOW_ORIGINS", default="*")
container.config.cors_allow_credentials.from_env(
    "CORS_ALLOW_CREDENTIALS",
    as_=lambda x: str_to_bool(x) if x != "" else False,
    default="False",
)
container.config.cors_allow_methods.from_env("CORS_ALLOW_METHODS", default="GET, POST")
container.config.cors_allow_headers.from_env("CORS_ALLOW_HEADERS", default="*")
container.config.debug_mode.from_env(
    "DEBUG_MODE",
    required=True,
    as_=lambda x: str_to_bool(x) if x != "" else False,
    default="False",
)
container.config.log_level.from_env(
    "LOG_LEVEL",
    required=True,
    as_=lambda x: x if x != "" else "INFO",
    default="INFO",
)
container.wire(modules=[__name__])

config_logging()
app = init_fastapi()
app.container = container

# Start the async event loop and ASGI server.
if __name__ == "__main__":
    asyncio.run(main())

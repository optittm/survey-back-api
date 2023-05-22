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
from routes.security import router as security_router
from utils.container import Container


@inject
def init_fastapi(prefix="/api/v1", config=Provide[Container.config]) -> FastAPI:
    logging.info("Init FastAPI app")
    # Creates the FastAPI instance inside the function to be able to use the config provider
    app = FastAPI(debug=config["debug_mode"])
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config["cors_allow_origins"].split(","),
        allow_credentials=config["cors_allow_credentials"],
        allow_methods=config["cors_allow_methods"].split(","),
        allow_headers=config["cors_allow_headers"].split(","),
    )
    app.include_router(comment_router, prefix=prefix)
    app.include_router(rule_router, prefix=prefix)
    # OAuth security is disabled if no key is present
    if config["secret_key"] != "":
        app.include_router(security_router, prefix=prefix)

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
container.config.survey_db.from_env(
    "SURVEY_DB", required=True, default="sqlite:///data/survey.sqlite3"
)
container.config.cors_allow_origins.from_env(
    "CORS_ALLOW_ORIGINS", required=True, default="*"
)
container.config.cors_allow_credentials.from_env(
    "CORS_ALLOW_CREDENTIALS", required=True, default=False
)
container.config.cors_allow_methods.from_env(
    "CORS_ALLOW_METHODS", required=True, default="GET, POST"
)
container.config.cors_allow_headers.from_env(
    "CORS_ALLOW_HEADERS", required=True, default="*"
)
container.config.secret_key.from_env("SECRET_KEY")
container.config.access_token_expire_minutes.from_env(
    "ACCESS_TOKEN_EXPIRE_MINUTES", as_=int, default=15
)
container.config.auth_url.from_env("AUTH_URL")
container.config.jwk_url.from_env("JWK_URL")
container.config.client_secrets.from_env("CLIENT_SECRETS")
container.config.debug_mode.from_env(
    "DEBUG_MODE", required=True, as_=bool, default=False
)
container.config.log_level.from_env("LOG_LEVEL", required=True, default="INFO")
container.wire(modules=[__name__])

config_logging()
app = init_fastapi()
app.container = container

# Start the async event loop and ASGI server.
if __name__ == "__main__":
    asyncio.run(main())

import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dependency_injector.wiring import Provide, inject
import uvicorn
from sqlalchemy.exc import ArgumentError
from pydbantic import Database

from models.comment import Comment
from models.project import Project, ProjectEncryption
from routes.comments import router as comment_router
from routes.rules import router as rule_router
from utils.container import Container


@inject
def init_fastapi(config=Provide[Container.config]) -> FastAPI:
    # Creates the FastAPI instance inside the function to be able to use the config provider
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config["cors_allow_origins"].split(","),
        allow_credentials=config["cors_allow_credentials"],
        allow_methods=config["cors_allow_methods"].split(","),
        allow_headers=config["cors_allow_headers"].split(","),
    )
    app.include_router(comment_router)
    app.include_router(rule_router)
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
    )
    # Running the server in the existing async loop
    # https://www.uvicorn.org/#config-and-server-instances
    server = uvicorn.Server(config)
    await server.serve()


@inject
async def init_db(
    config=Provide[Container.config],
    rules_config=Provide[Container.rules_config],
    sqlite_repo=Provide[Container.sqlite_repo],
):
    try:
        db = await Database.create(
            config["survey_db"], tables=[Project, Comment, ProjectEncryption]
        )
    except ArgumentError as e:
        raise Exception(f"Error from sqlalchemy : {str(e)}")

    project_names = rules_config.getProjectNames()
    for project_name in project_names:
        await sqlite_repo.create_project(Project(name=project_name))


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
container.config.debug_mode.from_env(
    "DEBUG_MODE", required=True, as_=bool, default=False
)
container.wire(modules=[__name__])

app = init_fastapi()
app.container = container

# Start the async event loop and ASGI server.
if __name__ == "__main__":
    asyncio.run(main())

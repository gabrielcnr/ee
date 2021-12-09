from pathlib import Path
from typing import Optional, Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from ee.models import EnvironmentDefinition, ApplicationEnvironment, Application
from ee.store import EnvSqliteGateway


class EnvDef(BaseModel):
    packages: Dict
    channels: Optional[List[str]] = Field(default_factory=list)
    env_id: Optional[str] = None


class AppEnvRequest(BaseModel):
    app: str
    env: str  # env name
    env_id: str  # hash


class AppEnvResponse(BaseModel):
    app: str
    env: str
    env_id: str


app = FastAPI()

# TODO: sort out this dependency here
store = EnvSqliteGateway.create(f"{Path('~/ee.db').expanduser()}")


@app.post("/envdefs/")
async def create_env_def(env_def: EnvDef):
    # TODO: do we need here 2 models, one pure Python and one Pydantic? I don't think so... ?
    env_def_dict = {"packages": env_def.packages}
    if env_def.channels:
        env_def_dict["channels"] = env_def.channels

    env_def = EnvironmentDefinition.from_dict(env_def_dict)
    store.save_env_def(env_def)
    return {"env_id": env_def.id}


@app.get("/envdefs/{env_id}")
async def get_env_def(env_id: str):
    env_def = store.get_env_def(env_id)
    env_def_api_model = EnvDef(packages=env_def.packages, channels=env_def.channels, env_id=env_def.id)
    return env_def_api_model.dict()


@app.post("/appenvs/")
async def configure_app_env(app_env_request: AppEnvRequest):
    """
    gotta send
        app name
        env name
        env id
    """
    # first we need to check if the given env_id is valid?
    env_def = store.get_env_def(app_env_request.env_id)
    if env_def is None:
        raise HTTPException(status_code=404, detail="env_id not found")

    app_env = ApplicationEnvironment(app=Application(name=app_env_request.app),
                                     env=app_env_request.env,
                                     env_def=env_def)

    store.save_app_env(app_env)
    return AppEnvResponse(app=app_env.app.name,
                          env=app_env.env,
                          env_id=app_env.env_def.id)


@app.get("/appenvs/")
async def get_env_def_for_app_env(app: str, env: str):
    if app_env := store.get_app_env(app, env):
        # channels is optional
        env_def_dict = {"env_id": app_env.env_def.id,
                          "packages": app_env.env_def.packages}
        if app_env.env_def.channels:
            env_def_dict["channels"] = app_env.env_def.channels
        return {"app": app,
                "env": env,
                "env_def": env_def_dict}
    else:
        raise HTTPException(status_code=404, detail=f"{(app, env) = } not found")


if __name__ == '__main__':
    import uvicorn

    if __name__ == "__main__":
        uvicorn.run("ee.server:app",
                    host="127.0.0.1",
                    port=8000,
                    log_level="info")
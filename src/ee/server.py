from pathlib import Path
from typing import Optional, Dict, List

from fastapi import FastAPI
from pydantic import BaseModel, Field

from ee.models import EnvironmentDefinition
from ee.store import EnvSqliteGateway


class EnvDef(BaseModel):
    packages: Dict
    channels: Optional[List[str]] = Field(default_factory=list)
    env_id: Optional[str] = None


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
    return {"env_spec": env_def.id}


@app.get("/envdefs/{env_id}")
async def get_env_def(env_id: str):
    env_def = store.get_env_def(env_id)
    env_def_api_model = EnvDef(packages=env_def.packages, channels=env_def.channels, env_id=env_def.id)
    return env_def_api_model.dict()

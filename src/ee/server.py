from typing import Optional, Dict, List

from fastapi import FastAPI
from pydantic import BaseModel, Field


class EnvDef(BaseModel):
    packages: Dict
    channels: Optional[List[str]] = Field(default_factory=list)


app = FastAPI()


@app.post("/envdefs/")
async def create_env_def(env_def: EnvDef):
    import pdb; pdb.set_trace()
    print(f"Creating EnvDef: {env_def}")


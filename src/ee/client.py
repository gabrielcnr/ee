import requests

from ee.server import EnvDef


class EEClient:
    """ Web client.
    """
    def __init__(self, base_url):
        self.base_url = base_url

    def new(self, env_def: EnvDef) -> str:
        url = f"{self.base_url}/envdefs"
        resp = requests.post(url, json=env_def.dict())
        resp.raise_for_status()
        env_def = resp.json()
        return env_def["id"]


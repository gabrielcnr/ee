import requests

from ee.config import EE_REQUEST_TIMEOUT
from ee.models import ApplicationEnvironment, Application, EnvironmentDefinition
from ee.server import EnvDef


class EEClient:
    """ Web client.
    """

    def __init__(self, base_url, client=None):
        self.base_url = base_url
        if client is None:
            self.client = requests

    def new_env_def(self, env_def: EnvDef) -> str:
        """ Send a request to create a new env def.
        """
        url = f"{self.base_url}/envdefs"
        resp = self.client.post(url, json=env_def.dict(), timeout=EE_REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        return data["env_id"]

    def get_env_def_for_app_env(self, app: str, env: str) -> ApplicationEnvironment:
        """ Send a request to fetch the env def for the pair (app, env).
        """
        # TODO: should return only the EnvironmentDefinition instead?
        url = f"{self.base_url}/appenvs?app={app}&env={env}"
        resp = self.client.get(url, timeout=EE_REQUEST_TIMEOUT)
        resp.raise_for_status()

        data = resp.json()

        env_def_dict = {"packages": data["env_def"]["packages"]}
        if data["env_def"].get("channels"):
            env_def_dict["channels"] = data["env_def"]["channels"]

        app_env = ApplicationEnvironment(app=Application(data["app"]),
                                         env=data["env"],
                                         env_def=EnvironmentDefinition.from_dict(env_def_dict))
        return app_env

    def set_env_def_for_app_env(self, app: str, env: str, env_id: str):
        url = f"{self.base_url}/appenvs/"
        payload = {"app": app,
                   "env": env,
                   "env_id": env_id}
        resp = self.client.post(url, json=payload, timeout=EE_REQUEST_TIMEOUT)
        resp.raise_for_status()

        # sanity check
        resp = resp.json()
        if resp["app"] != app:
            raise SanityCheckError(f"{resp['app'] = } != {app = }")

        if resp["env"] != env:
            raise SanityCheckError(f"{resp['env'] = } != {env = }")

        if resp["env_id"] != env_id:
            raise SanityCheckError(f"{resp['env_id'] = } != {env_id = }")


class SanityCheckError(Exception):
    pass

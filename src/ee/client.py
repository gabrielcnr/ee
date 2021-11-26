import requests

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
        resp = self.client.post(url, json=env_def.dict())
        resp.raise_for_status()
        env_def = resp.json()
        return env_def["id"]

    def get_env_def_for_app_env(self, app: str, env: str) -> ApplicationEnvironment:
        """ Send a request to fetch the env def for the pair (app, env).
        """
        url = f"{self.base_url}/appenvs?app={app}&env={env}"
        resp = self.client.get(url)
        resp.raise_for_status()

        data = resp.json()

        env_def_dict = {"packages": data["env_def"]["packages"],
                        "channels": data["env_def"]["channels"]}

        app_env = ApplicationEnvironment(app=Application(data["app"]),
                                         env=data["env"],
                                         env_def=EnvironmentDefinition.from_dict(env_def_dict))
        return app_env

    def set_env_def_for_app_env(self, app_env: ApplicationEnvironment):
        url = f"{self.base_url}/appenvs/"
        payload = {"app": app_env.app.name,
                   "env": app_env.env,
                   "env_id": app_env.env_def.id}
        resp = self.client.post(url, json=payload)
        resp.raise_for_status()

        # sanity check
        resp = resp.json()
        if resp["app"] != app_env.app.name:
            raise SanityCheckError(f"{resp['app'] = } != {app_env.app.name = }")

        if resp["env"] != app_env.env:
            raise SanityCheckError(f"{resp['env'] = } != {app_env.env = }")

        if resp["env_id"] != app_env.env_def.id:
            raise SanityCheckError(f"{resp['env_id'] = } != {app_env.env_def.id = }")


class SanityCheckError(Exception):
    pass

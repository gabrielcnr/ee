from typing import Dict

import pytest

from ee.models import AppEnvKey, ApplicationEnvironment, EnvironmentDefinition
from ee.store import EnvGateway
from ee.store.gateway import EnvID


class InMemoryEnvironmentStore(EnvGateway):
    def __init__(self):
        self.d = {
            "env_defs": {},
            "apps": {},
        }

    def save_env_def(self, env_def: EnvironmentDefinition):
        self.d["env_defs"][env_def.id] = env_def

    def get_env_def(self, env_id: str) -> EnvironmentDefinition:
        return self.d["env_defs"][env_id]

    def save_app_env(self, app_env: ApplicationEnvironment):
        apps = self.d["apps"]
        name = app_env.app.name
        env = app_env.env
        if name not in apps:
            apps[name] = {}
        if env not in apps[name]:
            apps[name][env] = []
        apps[name][env].append(app_env)

    def get_app_env(self, app_name: str, env_name: str) -> ApplicationEnvironment:
        return self.d["apps"][app_name][env_name][-1]

    def list_app_envs(self) -> Dict[AppEnvKey, EnvID]:
        return {
            AppEnvKey(app, env): self.d[app][env][-1]
            for app in self.d
            for env in self.d[app]
        }


@pytest.fixture
def in_memory_store():
    return InMemoryEnvironmentStore()

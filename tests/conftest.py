import pytest

from ee.models import EnvironmentDefinition, ApplicationEnvironment
from ee.store import EnvGateway


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


@pytest.fixture
def in_memory_store():
    return InMemoryEnvironmentStore()

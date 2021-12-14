from typing import List

from ee.deployers import DeploymentBackend
from ee.models import ApplicationEnvironment, EnvironmentDefinition
from ee.store import EnvGateway


class EnvironmentService:
    """
    The service knows about a DAO/Store and it also knows about
    a DeploymentBackend.

    The service could be split in two parts: one that serves
    the purpose to fulfill the admin use cases:
        - create a new environment definition
        - associate an environment definition to an
            (application, environment)
    and the other that serves the purpose to fulfill
    the normal user use case:
        - run something in the context of (application, environment)
    """

    def __init__(self, *, store: EnvGateway, deployment_backend: DeploymentBackend):
        self.store = store
        self.deployment_backend = deployment_backend

    def save_env_def(self, env_def: EnvironmentDefinition):
        self.store.save_env_def(env_def)

    def get_env_def(self, env_id: str) -> EnvironmentDefinition:
        return self.store.get_env_def(env_id)

    def save_app_env(self, app_env: ApplicationEnvironment):
        self.store.save_app_env(app_env)

    def get_app_env(self, app_name: str, env_name: str) -> ApplicationEnvironment:
        return self.store.get_app_env(app_name, env_name)

    def run(self, app_name: str, env_name: str, command: List[str]):
        app_env = self.get_app_env(app_name, env_name)
        self.deployment_backend.run(app_env.env_def, command)

from ee.models import EnvironmentDefinition, ApplicationEnvironment


class EnvironmentStore:

    def __init__(self, dao):
        self.dao = dao

    def save_env_def(self, env_def: EnvironmentDefinition):
        self.dao.save_env_def(env_def)

    def get_env_def(self, env_id: str) -> EnvironmentDefinition:
        return self.dao.get_env_def(env_id)

    def save_app_env(self, app_env: ApplicationEnvironment):
        self.dao.save_app_env(app_env)

    def get_app_env(self, app_name: str, env_name: str) -> ApplicationEnvironment:
        return self.dao.get_app_env(app_name, env_name)

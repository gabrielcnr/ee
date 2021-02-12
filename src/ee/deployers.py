import abc

from ee.models import EnvironmentDefinition


class DeployerBackendBase(abc.ABC):

    def __init__(self, use_long_id: bool = True):
        self.use_long_id = use_long_id

    def deploy(self, env_def: EnvironmentDefinition, command=None):
        env_id = env_def.long_id if self.use_long_id else env_def.id
        if not self.env_exists(env_id):
            self.create_env(env_def)
        if command:
            self.execute(env_id, command)

    @abc.abstractmethod
    def env_exists(self, env_id: str) -> bool:
        '''
        Check if environment with env_id already exists
        :param env_id:
        :return: True if environment exists, False otherwise
        '''

    @abc.abstractmethod
    def create_env(self, env_def: EnvironmentDefinition):
        '''
        Create an environment using the environment def
        :param env_def: Full environment definition
        :return:
        '''

    def execute(self, env_id: str, command: str):
        '''
        Given and environment id and command.
        Execute the command in the context of the environment
        :param env_id: Id of context environment
        :param command: Command to be executed under context environment
        :return:
        '''

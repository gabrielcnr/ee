import abc
import logging
from typing import List

from ee.models import EnvironmentDefinition

logger = logging.getLogger(__name__)


class DeploymentBackend(abc.ABC):
    def run(self, env_def: EnvironmentDefinition, command: List[str]):
        """
        This is the main public method.

        This is a template method which relies on the DeploymentBackend
        subclasses to provide the methods:
            .env_exists(env_id)
            .create_env(env_def)
            .execute(env_id, command_args)

        Args:
            env_def: the full EnvironmentDefinition object
            command: the list of command line arguments to be executed
                inside the environment
        """
        if not self.env_exists(env_def.id):
            logger.info(
                f"Environment not found: {env_def.id}"
                " - Please wait while EE creates the env ..."
            )
            if self.create_env(env_def):
                logger.info(f"Environment created successfully: {env_def.id}")
            else:
                logger.error(f"Failed to create environment: {env_def.id}")
        if command:
            self.execute(env_def.id, command)

    @abc.abstractmethod
    def env_exists(self, env_id: str) -> bool:
        """
        Checks whether an environment already exists or not, given
        its environment id.

        Args:
            env_id: hash/identifier for the environment

        Returns:
            True if the environment exists, False otherwise

        """

    @abc.abstractmethod
    def create_env(self, env_def: EnvironmentDefinition):
        """
        Create an environment using the environment def

        Args:
            env_def: Full environment definition

        Returns:
            None

        """

    @abc.abstractmethod
    def execute(self, env_id: str, command: List[str]):
        """
        Executes the given command inside the given environment.

        Args:
            env_id: hash/identifier for the environment
            command: list of command line arguments (including the main command)

        Returns:
            None

        """

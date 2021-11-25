from abc import ABC, abstractmethod

from ee.models import EnvironmentDefinition, ApplicationEnvironment


class EnvGateway(ABC):
    """
    Base / abstract class that provides the interface
    for the persistence / "database" layer for the
    environments.
    """

    @abstractmethod
    def save_env_def(self, env_def: EnvironmentDefinition):
        """
        Saves an environment definition on the database.

        Args:
            env_def: the EnvironmentDefinition containing
                the structure representing the packages and
                other metadata about the environment.

        Returns:
            None

        """

    @abstractmethod
    def get_env_def(self, env_id: str) -> EnvironmentDefinition:
        """

        Args:
            env_id:

        Returns:

        """

    @abstractmethod
    def save_app_env(self, app_env: ApplicationEnvironment):
        """

        Args:
            app_env:

        Returns:

        """

    @abstractmethod
    def get_app_env(self, app_name: str, env_name: str) -> ApplicationEnvironment:
        """

        Args:
            app_name:
            env_name:

        Returns:

        """
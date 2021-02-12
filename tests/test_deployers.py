from unittest.mock import Mock

from ee.deployers import DeployerBackendBase
from ee.models import EnvironmentDefinition
from test_models import TEST_INPUT


class MockDeployer(DeployerBackendBase):

    def env_exists(self):
        """this will be overwritten with a mock"""

    def create_env(self, env_def):
        """this will be overwritten with a mock"""


def test_create_env_first_time():
    deployer = MockDeployer()
    deployer.env_exists = Mock(return_value=False)
    deployer.create_env = Mock()
    deployer.execute = Mock()
    env_def = EnvironmentDefinition(TEST_INPUT)
    deployer.deploy(env_def)
    deployer.env_exists.assert_called_once_with(env_def.long_id)
    deployer.create_env.assert_called_once_with(env_def)
    deployer.execute.assert_not_called()


def test_create_env_first_time_id():
    deployer = MockDeployer(use_long_id=False)
    deployer.env_exists = Mock(return_value=False)
    deployer.create_env = Mock()
    deployer.execute = Mock()
    env_def = EnvironmentDefinition(TEST_INPUT)
    deployer.deploy(env_def)
    deployer.env_exists.assert_called_once_with(env_def.id)
    deployer.create_env.assert_called_once_with(env_def)
    deployer.execute.assert_not_called()


def test_create_env_second_time():
    deployer = MockDeployer()
    deployer.env_exists = Mock(return_value=True)
    deployer.create_env = Mock()
    deployer.execute = Mock()
    env_def = EnvironmentDefinition(TEST_INPUT)
    deployer.deploy(env_def)
    deployer.env_exists.assert_called_once_with(env_def.long_id)
    deployer.create_env.assert_not_called()
    deployer.execute.assert_not_called()


def test_deploy_env_with_command_first_time():
    deployer = MockDeployer()
    deployer.env_exists = Mock(return_value=False)
    deployer.create_env = Mock()
    deployer.execute = Mock()
    env_def = EnvironmentDefinition(TEST_INPUT)
    deployer.deploy(env_def, 'command.exe')
    deployer.env_exists.assert_called_once_with(env_def.long_id)
    deployer.create_env.assert_called_once_with(env_def)
    deployer.execute.assert_called_once_with(env_def.long_id, 'command.exe')

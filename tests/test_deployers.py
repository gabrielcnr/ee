from ee.deployers import DeploymentBackend
from ee.models import EnvironmentDefinition


class InMemoryDeploymentBackend(DeploymentBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # we do not use dict here because we want to check if env is not created twice
        self.envs = []
        self.executed_commands = []

    def env_exists(self, env_id):
        for stored_env_id, _ in self.envs:
            if stored_env_id == env_id:
                return True
        return False

    def create_env(self, env_def):
        self.envs.append((env_def.id, env_def))

    def execute(self, env_id, command):
        self.executed_commands.append((env_id, command))


def test_deployer_can_run_something():
    deployer = InMemoryDeploymentBackend()

    assert [] == deployer.envs
    assert [] == deployer.executed_commands

    env_def = EnvironmentDefinition('{"packages": {"foo": "1.2.3"}}')
    cmd_args = ["command-main", "arg1", "--option=foo"]
    deployer.run(env_def, cmd_args)

    assert [("92f9752", env_def)] == deployer.envs
    assert [("92f9752", cmd_args)] == deployer.executed_commands

    # If you run something on the environment for the second time
    # it doesn't create a new environment
    cmd_args_2 = ["other-command"]
    deployer.run(env_def, cmd_args_2)

    assert [("92f9752", env_def)] == deployer.envs
    assert [
        ("92f9752", cmd_args),
        ("92f9752", cmd_args_2),
    ] == deployer.executed_commands

    # Now we want to use a brand new environment
    env_def_2 = EnvironmentDefinition('{"packages": {"bar": "4.5.6"}}')
    cmd_args_3 = ["foobar", "123"]
    deployer.run(env_def_2, cmd_args_3)

    # We will check that environment was created - new deployment!
    assert [("92f9752", env_def), ("95e885b", env_def_2)] == deployer.envs
    expected_runs = [
        ("92f9752", cmd_args),
        ("92f9752", cmd_args_2),
        ("95e885b", cmd_args_3),
    ]
    assert expected_runs == deployer.executed_commands

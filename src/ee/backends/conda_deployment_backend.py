from typing import List

from ee.deployers import DeploymentBackend
from ee.models import EnvironmentDefinition
import subprocess


class CondaDeploymentBackend(DeploymentBackend):

    CONDA_CMD = "conda"

    def create_env(self, env_def: EnvironmentDefinition):
        # TODO: support for custom channels
        create_command = f"{self.CONDA_CMD} create -n {env_def.id} -y".split()
        for package_name, package_version in env_def.packages.items():
            create_command.append(f'"{package_name}=={package_version}"')
        p = subprocess.run(create_command, shell=False)
        return p.returncode == 0

    def env_exists(self, env_id: str) -> bool:
        command = f"{self.CONDA_CMD} list -n {env_id}".split()
        p = subprocess.run(command, shell=False)
        return p.returncode == 0

    def execute(self, env_id: str, command: List[str]):
        if isinstance(command, str):
            command = [command]

        run_command = f"{self.CONDA_CMD} run --no-capture-output -n {env_id}".split()
        run_command += command

        # TODO: decide what to do with stdout and stderr
        #       we want the run commands to be detached
        #       and non-blocking
        p = subprocess.Popen(run_command, shell=False)
        return p


class MambaDeploymentBackend(CondaDeploymentBackend):
    CONDA_CMD = "mamba"

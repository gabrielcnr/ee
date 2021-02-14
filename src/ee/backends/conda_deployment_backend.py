from typing import List

from ee.deployers import DeploymentBackend
from ee.models import EnvironmentDefinition
import subprocess


class CondaDeploymentBackend(DeploymentBackend):

    def create_env(self, env_def: EnvironmentDefinition):
        create_command = f"conda create -n {env_def.id} -y".split()
        for package_name, package_version in env_def.packages.items():
            create_command.append(f'"{package_name}=={package_version}"')
        subprocess.run(create_command, shell=True)

    def env_exists(self, env_id: str) -> bool:
        command = f"conda list -n {env_id}".split()
        p = subprocess.run(command, shell=True)
        return p.returncode == 0

    def execute(self, env_id: str, command: List[str]):
        run_command = f"conda run -n {env_id}".split()
        run_command += command

        # TODO: decide what to do with stdout and stderr
        #       we want the run commands to be detached
        #       and non-blocking
        p = subprocess.Popen(run_command, shell=True)
        return p
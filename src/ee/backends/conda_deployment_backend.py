import logging
import os
import sys
from typing import List

from ee.config import EE_DEBUG
from ee.deployers import DeploymentBackend
from ee.models import EnvironmentDefinition
import subprocess

logger = logging.getLogger(__name__)

# TODO: understand why different behaviour on Windows?
on_win = sys.platform.startswith("win")

SHELL = on_win


class CondaDeploymentBackend(DeploymentBackend):

    CONDA_CMD = "conda"

    def create_env(self, env_def: EnvironmentDefinition):
        # TODO: support for custom channels
        create_command = f"{self.CONDA_CMD} create -n {env_def.id} -y".split()
        for conda_channel in env_def.channels:
            create_command += ["-c", conda_channel]
        for package_name, package_version in env_def.packages.items():
            create_command.append(f'"{package_name}=={package_version}"')
        if EE_DEBUG:
            logger.debug(f"Executing: {create_command}")
        capture_output = not EE_DEBUG
        p = subprocess.run(create_command, shell=SHELL, capture_output=capture_output)
        return p.returncode == 0

    def env_exists(self, env_id: str) -> bool:
        command = f"{self.CONDA_CMD} list -n {env_id}".split()
        capture_output = not EE_DEBUG
        p = subprocess.run(command, shell=SHELL, capture_output=capture_output)
        return p.returncode == 0

    def execute(self, env_id: str, command: List[str]):
        if isinstance(command, str):
            command = [command]

        # As of Dec21 conda 4.11.0 had the behaviour of when running "conda run -n env python ..."
        # with no environment activated or from the base environment, it worked as expected,
        # picking up and calling python from the .../envs/env/bin/python of the environment.
        # However if you had another environment activated and called
        # "conda run -n env python ..." it would pick up python from the base environment
        # instead (wrong!)
        # So a temp workaround is to apply some kind of "inception" here and ask
        # conda to run conda run (itself) from the base environment then pointing to "env"
        # $ conda run -n base conda run -n env python ...
        # Another solution to consider here is to have conda as an explicit dependency
        # for ee, which then would make it possible to use the conda python api calls.
        # This would require some kind of management to ensure multiple conda installations
        # can live in harmony in the same machine / user area.

        run_command = f"{self.CONDA_CMD} run --no-capture-output -n base " \
                      f"{self.CONDA_CMD} run --no-capture-output -n {env_id}".split()
        run_command += command

        # TODO: decide what to do with stdout and stderr
        #       we want the run commands to be detached
        #       and non-blocking
        p = subprocess.Popen(run_command, shell=SHELL)
        return p


class MambaDeploymentBackend(CondaDeploymentBackend):

    CONDA_CMD = "mamba"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        os.environ["MAMBA_NO_BANNER"] = "1"

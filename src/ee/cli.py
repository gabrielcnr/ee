"""
ee - Command Line Interface (USER)
"""

import typer

from ee.backends.conda_deployment_backend import MambaDeploymentBackend
from ee.client import EEClient

app = typer.Typer()

client = EEClient("http://localhost:5000")

backend = MambaDeploymentBackend()


@app.command()
def run(app: str, env: str, command: str):
    app_env = client.get_env_def_for_app_env(app, env)
    backend.run(app_env.env_def, command)


if __name__ == "__main__":
    app()

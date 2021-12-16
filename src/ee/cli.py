"""
ee - Command Line Interface (USER)
"""
from typing import List

import click
import typer

from ee.backends.conda_deployment_backend import MambaDeploymentBackend
from ee.client import EEClient

app = typer.Typer()

client = EEClient("http://localhost:5000")

backend = MambaDeploymentBackend()


@app.callback()
def callback():
    """
    Environments Everywhere is an environment manager that allows
    multiple deployments for the same application pointing to
    different environments (package configurations), in a way
    that is abstracted from the end-user.
    """


@click.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.option("-a", "--app", required=True, help="Application name")
@click.option("-e", "--env", required=True, help="Environment name (e.g.: prod)")
@click.argument("command", required=True, nargs=-1, type=click.UNPROCESSED)
def run(app: str, env: str, command: List[str]):
    """ Run a command inside the context of an (app, env).

    You must specify a command.

    Example of usage:

    $ ee run -a reports -e prod run-report -n"DAILY REPORT"

    """
    app_env = client.get_env_def_for_app_env(app, env)
    backend.run(app_env.env_def, command)


typer_click_object = typer.main.get_command(app)

typer_click_object.add_command(run, "run")


def main():
    typer_click_object()


if __name__ == "__main__":
    main()

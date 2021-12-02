"""
ee - Command Line Interface (ADMIN)

Sub-commands:

    save
    show
    run

"""
from pathlib import Path

import typer

from ee.client import EEClient
from ee.models import EnvironmentDefinition
from ee.server import EnvDef

app = typer.Typer()

client = EEClient("http://localhost:8000")

@app.command()
def new(filename: Path):
    """ Add a new Env Spec based on the given filename.

    It must be a JSON file defining "packages".
    Optionally it may define "channels".

    E.g.:

    # my_env.json
    {
        "packages": {
            "pandas": ">=1.2.1,<1.3",
            "python": "3.8"
        }
    }

    $ ee new my_env.json
    """
    temp = EnvironmentDefinition(filename.open().read())
    env_def = EnvDef(packages=temp.packages, channels=temp.channels)
    typer.echo(f"Read EnvironmentDefinition from file: {filename}")
    env_id = client.new_env_def(env_def)
    typer.echo(f"New Environment defined. ID: {env_id}")


@app.command()
def assoc(app: str, env: str, env_id: str):
    client.set_env_def_for_app_env(app=app, env=env, env_id=env_id)
    typer.echo(f"Env: {env} for app: {app} is now set to: {env_id}")


@app.command()
def show(app: str, env: str):
    app_env = client.get_env_def_for_app_env(app=app, env=env)
    typer.echo(f"App: {app_env.app.name} - Env: {app_env.env}")
    typer.echo(f"ID: {app_env.env_def.id}")


# TODO: command to list all env defs
# TODO: command to remove/delete an env def
# TODO: command to list all (app, envs)
# TODO: command to show history of an (app, env)


if __name__ == "__main__":
    app()
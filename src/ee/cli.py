"""
ee - Command Line Interface

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
    result = client.new_env_def(env_def)
    # typer.echo(f"Long ID: {env_def.long_id}")
    # typer.echo(f"Short ID: {env_def.id}")


@app.command()
def assoc(app: str, env_hash: str, env_name: str):
    typer.echo(f"{app} {env_hash!r} {env_name!r}")


if __name__ == "__main__":
    app()
"""
ee - Command Line Interface (ADMIN)

Sub-commands:

    save
    show
    run

"""
from pathlib import Path
from typing import Optional

import typer
from pygments import formatters, highlight, lexers
from requests import HTTPError

from ee.client import EEClient
from ee.models import EnvironmentDefinition
from ee.server import EnvDef

app = typer.Typer()

client = EEClient("http://localhost:5000")


@app.command()
def new(filename: Path):
    """Add a new Env Spec based on the given filename.

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
    typer.secho(f"New Environment defined. ID: {env_id}", fg="yellow")


@app.command()
def assoc(app: str, env: str, env_id: str):
    client.set_env_def_for_app_env(app=app, env=env, env_id=env_id)
    typer.secho(f"Set: <<{app}, {env}>> --> {env_id}", fg="yellow")


@app.command()
def show(app: str, env: str, details: Optional[bool] = None):
    """
    Show the current Env ID mapped to a given (app, env).

    If --details is used, then it will show the environment definition
    with the packages specification for the currently mapped env.
    """
    details = details or typer.Option(False, help="Show env def details")
    try:
        app_env = client.get_env_def_for_app_env(app=app, env=env)
    except HTTPError as err:
        typer.secho(f"{err}", fg="yellow")
        if (response := getattr(err, "response", None)) is not None:
            if "detail" in (details := response.json()):
                typer.secho(f"Detail: {details['detail']}", fg="yellow")
    else:
        banner = (
            f"App: {app_env.app.name} - Env: {app_env.env}"
            f" ---> EnvID: {app_env.env_def.id}"
        )
        typer.secho("\n" + banner, fg="yellow")
        if details:
            typer.echo("-" * min(70, len(banner) + 1) + "\n")
            env_def_json = app_env.env_def.to_json(pretty=True)
            pretty_json = highlight(
                env_def_json, lexers.JsonLexer(), formatters.TerminalFormatter()
            )
            typer.echo(pretty_json)
        # typer.echo(f"Launch this environment with:\nee {app} {env")  # hint


@app.command("list")
def list_envs():
    """List all (app, env)"""
    for item in (envs := client.list_envs()):
        app, env = item["app_env"]
        env_id = item["env_id"]
        print(f"({app}, {env}) --> {env_id}")
    print(f"\nTotal: {len(envs)}")


# TODO: command to list all env defs
# TODO: command to remove/delete an env def
# TODO: command to show history of an (app, env)
# TODO: disable


if __name__ == "__main__":
    app()

import pytest
from test_deployers import InMemoryDeploymentBackend

from ee.models import Application, ApplicationEnvironment, EnvironmentDefinition
from ee.service import EnvironmentService


@pytest.fixture
def env_service(in_memory_store):
    deployment_backend = InMemoryDeploymentBackend()
    env_service = EnvironmentService(
        store=in_memory_store, deployment_backend=deployment_backend
    )
    return env_service


def test_env_service_roundtrip_persistence_for_env_def(env_service: EnvironmentService):
    raw = '{"packages": {"foo": "1.2.3"}}'
    env_def = EnvironmentDefinition(raw)

    env_service.save_env_def(env_def)

    env_def_returned = env_service.get_env_def(env_def.id)
    assert env_def_returned == env_def


def test_env_service_multiple_env_defs(env_service: EnvironmentService):
    for n in [4, 5, 6]:
        _ = EnvironmentDefinition('{"packages": {"foo": "1.2.%s"}}' % n)
        env_service.save_env_def(_)

    env_id = EnvironmentDefinition('{"packages": {"foo": "1.2.5"}}').id

    env_def = env_service.get_env_def(env_id)

    assert env_def.id == env_id
    assert env_def.packages == {"foo": "1.2.5"}


def test_associate_application_environment(env_service: EnvironmentService):
    env_def = EnvironmentDefinition('{"packages": {"foo": "9.8.7"}}')
    env_service.save_env_def(env_def)

    app = Application(name="my-app")

    app_env = ApplicationEnvironment(app=app, env="prod", env_def=env_def)

    env_service.save_app_env(app_env)


def test_application_environment_roundtrip(env_service: EnvironmentService):
    env_def = EnvironmentDefinition('{"packages": {"foo": "9.8.7"}}')
    env_service.save_env_def(env_def)

    app = Application(name="my-app")

    app_env = ApplicationEnvironment(app=app, env="prod", env_def=env_def)

    env_service.save_app_env(app_env)

    app_env_returned = env_service.get_app_env("my-app", "prod")

    assert app_env_returned.env_def.packages == {"foo": "9.8.7"}


def test_run(env_service: EnvironmentService):
    # First we create an environment definition
    env_def = EnvironmentDefinition('{"packages": {"foo": "9.8.7"}}')
    env_service.save_env_def(env_def)

    # Then we associate it to an (application, environment)
    app = Application(name="some_app")
    app_env = ApplicationEnvironment(app=app, env="uat", env_def=env_def)
    env_service.save_app_env(app_env)

    # Finally we ask the service to run something on that (app, env)
    env_service.run("some_app", "uat", ["hello", "world"])

    # We can then run the asserts against the deployment backend inside our service
    assert [("b262deb", env_def)] == env_service.deployment_backend.envs
    assert [
        ("b262deb", ["hello", "world"])
    ] == env_service.deployment_backend.executed_commands

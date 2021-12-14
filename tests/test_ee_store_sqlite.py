import json

import pytest

from ee.models import (
    AppEnvKey,
    Application,
    ApplicationEnvironment,
    EnvironmentDefinition,
)
from ee.store import EnvSqliteGateway
from ee.store._ee_store_sqlite import AppEnv, EnvDef, EnvironmentPersistenceError


@pytest.fixture
def gateway():
    return EnvSqliteGateway.create()


@pytest.fixture
def simple_env_def():
    env_def_dict = {"packages": {"pandas": ">=1.1,<1.2"}}
    raw = json.dumps(env_def_dict)
    env_def = EnvironmentDefinition(raw)
    return env_def


def test_save_env_def(gateway, simple_env_def):
    # Database state is empty
    assert gateway.session.query(EnvDef).all() == []

    gateway.save_env_def(simple_env_def)

    # Database state contains one env def
    (env_def_back_from_db,) = gateway.session.query(EnvDef)

    assert env_def_back_from_db.id == simple_env_def.id
    assert env_def_back_from_db.long_hash == simple_env_def.long_id
    assert env_def_back_from_db.env_def == simple_env_def.env_def


def test_get_env_def(gateway, simple_env_def):
    gateway.session.add(
        EnvDef(id="266f486", long_hash="aaa", env_def={"packages": {"pkg-a": "1.2"}})
    )
    gateway.session.commit()

    env_def_returned = gateway.get_env_def("266f486")
    assert env_def_returned.env_def == {"packages": {"pkg-a": "1.2"}}
    assert env_def_returned.packages == {"pkg-a": "1.2"}
    assert env_def_returned.channels == []
    assert (
        env_def_returned.long_id
        == "266f4866bd695aa64c0a93e0bc90348f7c4f8d50632fbaf208f268027ff54d91"
    )


def test_save_and_get_roundtrip(gateway, simple_env_def):
    gateway.save_env_def(simple_env_def)
    env_def_returned = gateway.get_env_def(simple_env_def.id)
    assert env_def_returned == simple_env_def


def test_try_to_get_env_that_does_not_exist(gateway):
    assert gateway.get_env_def("some-env-id") is None


def test_save_and_get_exception(gateway, simple_env_def):
    gateway.session.add(
        EnvDef(id="a", long_hash="aaa", env_def={"packages": {"pkg-a": "1.2"}})
    )
    gateway.session.commit()

    with pytest.raises(EnvironmentPersistenceError):
        gateway.get_env_def("a")


def test_save_app_env(gateway, simple_env_def):
    gateway.save_env_def(simple_env_def)

    assert gateway.session.query(AppEnv).all() == []

    app_env = ApplicationEnvironment(
        env="test-env", app=Application(name="test-app"), env_def=simple_env_def
    )

    gateway.save_app_env(app_env)

    # Assertions are made against ORM database objects
    (app_env_orm,) = gateway.session.query(AppEnv).all()  # only one (unpacking)

    assert app_env_orm.app == "test-app"
    assert app_env_orm.env_name == "test-env"
    assert app_env_orm.env_def.id == simple_env_def.id
    assert app_env_orm.env_def.env_def == simple_env_def.env_def


def test_get_app_env(gateway, simple_env_def):
    gateway.save_env_def(simple_env_def)
    app_env = ApplicationEnvironment(
        env="test-env", app=Application(name="test-app"), env_def=simple_env_def
    )

    gateway.save_app_env(app_env)

    app_env_returned = gateway.get_app_env("test-app", "test-env")

    assert isinstance(app_env_returned, ApplicationEnvironment)
    assert app_env_returned.app.name == "test-app"
    assert app_env_returned.env == "test-env"
    assert app_env_returned.env_def.id == "0f89efe"
    assert app_env_returned.env_def.packages == {"pandas": ">=1.1,<1.2"}


def test_list_app_envs(gateway):
    gateway.session.add_all(
        [
            AppEnv(app="app1", env_name="uat", env_def_id="envdef1"),
            AppEnv(app="app1", env_name="uat", env_def_id="envdef2"),
            AppEnv(app="app2", env_name="uat", env_def_id="envdef1"),
            AppEnv(app="app2", env_name="uat", env_def_id="envdef2"),
            AppEnv(app="app2", env_name="uat", env_def_id="envdef3"),
            AppEnv(app="app2", env_name="prod", env_def_id="envdef1"),
            AppEnv(app="app2", env_name="prod", env_def_id="envdef2"),
            AppEnv(app="app3", env_name="prod", env_def_id="envdef9"),
        ]
    )
    gateway.session.commit()

    expected = {
        AppEnvKey(app="app1", env="uat"): "envdef2",
        AppEnvKey(app="app2", env="uat"): "envdef3",
        AppEnvKey(app="app2", env="prod"): "envdef2",
        AppEnvKey(app="app3", env="prod"): "envdef9",
    }

    assert expected == gateway.list_app_envs()

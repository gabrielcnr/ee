import pytest
from fastapi.testclient import TestClient

import ee.store
from ee.server import AppEnvRequest, EnvDef, app
from ee.store import EnvSqliteGateway

client = TestClient(app)


@pytest.fixture(autouse=True)
def test_gateway(mocker, tmp_path):
    """Can't use in-memory sqlite database with multithreaded code."""
    mocker.patch.object(ee.server, "store", EnvSqliteGateway.create(tmp_path / "ee.db"))
    yield


def test_create_env_def():
    env_def_payload = EnvDef(packages={"pkg-a": "<2.0", "pkg-b": "1.8.1"}).dict()
    response = client.post("/envdefs/", json=env_def_payload)
    assert response.status_code == 200
    assert response.json() == {"env_id": "f3538af"}


def test_get_env_def():
    # Add one
    env_def_payload = EnvDef(packages={"pkg-a": "<2.0", "pkg-b": "1.8.1"}).dict()
    client.post("/envdefs/", json=env_def_payload)

    # Retrieve it back
    response = client.get("/envdefs/f3538af")
    assert response.status_code == 200
    assert response.json() == {
        "env_id": "f3538af",
        "packages": {"pkg-a": "<2.0", "pkg-b": "1.8.1"},
        "channels": [],
    }


def test_configure_app_env():
    # Add one env def
    env_def_payload = EnvDef(packages={"pkg-a": "<2.0", "pkg-b": "1.8.1"}).dict()
    client.post("/envdefs/", json=env_def_payload)

    app_env_payload = AppEnvRequest(
        app="some-app", env="some-env", env_id="f3538af"
    ).dict()
    resp = client.post("/appenvs/", json=app_env_payload)

    assert resp.status_code == 200
    assert resp.json() == {"app": "some-app", "env": "some-env", "env_id": "f3538af"}


def test_get_env_def_for_app_env():
    pkg_specs = [
        {"pkg-a": "<2.0", "pkg-b": "1.8.1"},  # f3538af
        {"pkg-a": ">=2.0,<2.1", "pkg-b": "2.0"},  # 3c3f3fc
    ]
    for pkg_spec in pkg_specs:
        env_def_payload = EnvDef(packages=pkg_spec).dict()
        client.post("/envdefs/", json=env_def_payload)

    # Associate (some-app, some-env) --> 3c3f3fc
    for env_id in ["f3538af", "3c3f3fc"]:
        app_env_payload = AppEnvRequest(
            app="some-app", env="some-env", env_id=env_id
        ).dict()
        client.post("/appenvs/", json=app_env_payload)

    # Associate (some-app, another-env) --> f3538af
    app_env_payload = AppEnvRequest(
        app="some-app", env="another-env", env_id="f3538af"
    ).dict()
    client.post("/appenvs/", json=app_env_payload)

    #
    # # Let's check ...
    def assert_env_def(app, env, expected):
        r = client.get(f"/appenvs/?app={app}&env={env}")
        assert r.status_code == 200
        resp = r.json()
        assert resp["env_def"]["env_id"] == expected

    assert_env_def("some-app", "some-env", "3c3f3fc")

    assert_env_def("some-app", "another-env", "f3538af")

import pytest
from fastapi.testclient import TestClient

import ee.store
from ee.server import app, EnvDef, AppEnvRequest
from ee.store import EnvSqliteGateway

client = TestClient(app)


@pytest.fixture(autouse=True)
def test_gateway(mocker, tmp_path):
    """ Can't use in-memory sqlite database with multithreaded code.
    """
    mocker.patch.object(ee.server, "store", EnvSqliteGateway.create(tmp_path / "ee.db"))
    yield


def test_create_env_def():
    env_def_payload = EnvDef(packages={"pkg-a": "<2.0", "pkg-b": "1.8.1"}).dict()
    response = client.post("/envdefs/", json=env_def_payload)
    assert response.status_code == 200
    assert response.json() == {"env_spec": "f3538af"}


def test_get_env_def():
    # Add one
    env_def_payload = EnvDef(packages={"pkg-a": "<2.0", "pkg-b": "1.8.1"}).dict()
    client.post("/envdefs/", json=env_def_payload)

    # Retrieve it back
    response = client.get("/envdefs/f3538af")
    assert response.status_code == 200
    assert response.json() == {"env_id": "f3538af",
                               "packages": {"pkg-a": "<2.0", "pkg-b": "1.8.1"},
                               "channels": []}


def test_configure_app_env():
    # Add one env def
    env_def_payload = EnvDef(packages={"pkg-a": "<2.0", "pkg-b": "1.8.1"}).dict()
    client.post("/envdefs/", json=env_def_payload)

    app_env_payload = AppEnvRequest(app="some-app", env="some-env", env_id="f3538af").dict()
    resp = client.post("/appenvs/", json=app_env_payload)

    assert resp.status_code == 200
    assert resp.json() == {"app": "some-app",
                           "env": "some-env",
                           "env_id": "f3538af"}

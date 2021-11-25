import pytest
from fastapi.testclient import TestClient

import ee.store
from ee.server import app, EnvDef
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

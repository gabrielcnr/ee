import pytest
import responses

from ee.client import EEClient
from ee.models import Application, ApplicationEnvironment, EnvironmentDefinition


@pytest.fixture
def mock_responses():
    with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
        yield rsps


@pytest.fixture
def client():
    yield EEClient("http://baseurl")


def test_get_env_def_for_app_env(mock_responses, client):
    mock_responses.add(
        responses.GET,
        "http://baseurl/appenvs?app=myapp&env=myenv",
        json={
            "app": "myapp",
            "env": "myenv",
            "env_def": {
                "env_id": "abcd1234",
                "packages": {
                    "pkg-a": "1.0",
                    "pkg-b": ">2.0,<3",
                },
                "channels": [],
            },
        },
        status=200,
    )

    app_env = client.get_env_def_for_app_env("myapp", "myenv")

    expected_app_env = ApplicationEnvironment(
        app=Application("myapp"),
        env="myenv",
        env_def=EnvironmentDefinition.from_dict(
            {"packages": {"pkg-a": "1.0", "pkg-b": ">2.0,<3"}}
        ),
    )
    assert expected_app_env == app_env


def test_set_env_def_for_app_env(mock_responses, client):
    mock_responses.add(
        responses.POST,
        "http://baseurl/appenvs/",
        json={
            "app": "testapp",
            "env": "testenv",
            "env_id": "b1ce87e",
        },
        status=200,
    )

    client.set_env_def_for_app_env(app="testapp", env="testenv", env_id="b1ce87e")

    (call,) = mock_responses.calls
    request = call.request

    assert request.method == "POST"
    assert request.url == "http://baseurl/appenvs/"
    assert request.body == b'{"app": "testapp", "env": "testenv", "env_id": "b1ce87e"}'

from ee.backends.conda_deployment_backend import SHELL, CondaDeploymentBackend
from ee.models import Application, ApplicationEnvironment, EnvironmentDefinition
from ee.service import EnvironmentService


def test_conda_deployment_backend_run_command(mocker, in_memory_store):
    backend = CondaDeploymentBackend()

    service = EnvironmentService(store=in_memory_store, deployment_backend=backend)

    env_def = EnvironmentDefinition(
        '{"packages": {"foo": "1.2.3", "bar": ">=4.5.1,<5.0"}}'
    )
    service.save_env_def(env_def)

    app = Application(name="my-app")
    app_env = ApplicationEnvironment(app=app, env="prod", env_def=env_def)
    service.save_app_env(app_env)

    mock_subprocess_run = mocker.patch(
        "ee.backends.conda_deployment_backend.subprocess.run", autospec=True
    )
    mock_subprocess_Popen = mocker.patch(
        "ee.backends.conda_deployment_backend.subprocess.Popen", autospec=True
    )

    service.run("my-app", "prod", ["foo", "bar"])

    # This should trigger 3 calls to subprocess.run
    # 1) for checking if the environment already exists
    # 2) for creating the environment the first time
    # 3) for running the command
    assert mock_subprocess_run.call_args_list == [
        mocker.call(
            ["conda", "list", "-n", "412b992"], shell=SHELL, capture_output=True
        ),
        mocker.call(
            'conda create -n 412b992 -y "foo=1.2.3" "bar>=4.5.1,<5.0"'.split(),
            shell=SHELL,
            capture_output=True,
        ),
    ]

    mock_subprocess_Popen.assert_has_calls(
        [
            mocker.call(
                "conda run --no-capture-output -n base "
                "conda run --no-capture-output -n 412b992 foo bar".split(),
                shell=SHELL,
            ),
        ]
    )

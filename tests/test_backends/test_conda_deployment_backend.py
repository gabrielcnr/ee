from ee.backends.conda_deployment_backend import CondaDeploymentBackend
from ee.models import EnvironmentDefinition, Application, ApplicationEnvironment
from ee.service import EnvironmentService


def test_conda_deployment_backend_run_command(mocker, in_memory_store):
    backend = CondaDeploymentBackend()

    service = EnvironmentService(store=in_memory_store,
                                 deployment_backend=backend)

    env_def = EnvironmentDefinition('{"packages": {"foo": "1.2.3", "bar": "4.5.6"}}')
    service.save_env_def(env_def)

    app = Application(name="my-app")
    app_env = ApplicationEnvironment(app=app, env="prod", env_def=env_def)
    service.save_app_env(app_env)

    mock_subprocess_run = mocker.patch("ee.backends.conda_deployment_backend.subprocess.run", autospec=True)
    mock_subprocess_Popen = mocker.patch("ee.backends.conda_deployment_backend.subprocess.Popen", autospec=True)

    service.run("my-app", "prod", ["foo", "bar"])

    # This should trigger 3 calls to subprocess.run
    # 1) for checking if the environment already exists
    # 2) for creating the environment the first time
    # 3) for running the command
    assert mock_subprocess_run.call_args_list == [
        mocker.call(['conda', 'list', '-n', '88183ec'], shell=True),
        mocker.call('conda create -n 88183ec -y "foo==1.2.3" "bar==4.5.6"'.split(), shell=True),
    ]

    mock_subprocess_Popen.assert_has_calls([
        mocker.call("conda run -n 88183ec foo bar".split(), shell=True),
    ])


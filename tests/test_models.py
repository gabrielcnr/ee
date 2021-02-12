import pytest

from ee.models import EnvironmentDefinition

TEST_INPUT = """\
{
    "packages": {
        "foo": "1.2.3"
    }
}
"""
def test_create_simple_environment_definition():
    env_def = EnvironmentDefinition(TEST_INPUT)
    assert env_def.id == "92f9752"
    assert env_def.long_id == "92f97528f268a88eb83866586f9281634d4b93b2c98503326ba99363f55c0e0c"
    assert env_def.packages == {"foo": "1.2.3"}
    assert env_def.channels == []


INPUT_WITH_CHANNELS = """\
{
    "packages": {
        "foo": "1.2.3"
    },
    "channels": [
        "chan1",
        "chan2"
    ]
}
"""
def test_create_environment_with_channels_specified():
    env_def = EnvironmentDefinition(INPUT_WITH_CHANNELS)
    assert env_def.channels == ["chan1", "chan2"]
    assert env_def.id == "22594ba"


def test_create_invalid_environment_definition_missing_packages():
    with pytest.raises(ValueError, match="You must specify \"packages\" in your "
                                         "environment definition."):
        EnvironmentDefinition("{}")


def test_create_invalid_environment_definition_blank_packages():
    with pytest.raises(ValueError, match="Your packages cannot be blank/empty in your "
                                         "environment definition."):
        EnvironmentDefinition('{"packages": {}}')

import hashlib
import json
from typing import Dict, List


# TODO: should we use Pydantic?

class EnvironmentDefinition:
    def __init__(self, raw_def: str):
        env_def = self.parse_env_def(raw_def)
        self.raw_def = raw_def
        self.env_def = env_def
        self._long_id = None

    def parse_env_def(self, raw_def: str) -> Dict:
        env_def = json.loads(raw_def)
        if "packages" not in env_def:
            raise ValueError("You must specify \"packages\" in your "
                             "environment definition.")
        if not env_def["packages"]:
            raise ValueError("Your packages cannot be blank/empty in your "
                             "environment definition.")
        return env_def

    @property
    def id(self) -> str:
        """
        Short hash/id for this environment.
        """
        return self.long_id[:7]

    @property
    def long_id(self) -> str:
        """
        Long hash/id for this environment.
        """
        if self._long_id is None:
            self._long_id = hashlib.sha256(json.dumps(
                self.env_def, sort_keys=True).encode()).hexdigest()
        return self._long_id

    @property
    def packages(self) -> Dict:
        """
        Return:
            packages that define this environment.
            This is required.

        Example:
            {"pandas": "0.25.3", "sqlalchemy": "1.0.0"}
        """
        return self.env_def["packages"]

    @property
    def channels(self) -> List:
        """
        Return:
            list of additional conda channels.
            This is optional.
            If it hasn't been specified on the environment definition
            then it will return an empty list.
        """
        return self.env_def.get("channels", [])

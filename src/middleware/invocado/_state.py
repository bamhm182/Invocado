import pathlib
import requests

from typing import Union


class State(object):
    def __init__(self):
        self._config_dir = None
        self._guacamose_host = None
        self._guacamole_password = None
        self._guacamole_username = None
        self._terraform_dir = None
        self._terraform_repo = None
        self._wol_ip = None
        self._wol_port = None

    @property
    def config_dir(self) -> pathlib.PosixPath:
        if self._config_dir is None:
            self._config_dir = pathlib.Path('~/.config/invocado').expanduser().resolve()
        if self._config_dir:
            self._config_dir.mkdir(parents=True, exist_ok=True)
        return self._config_dir

    @config_dir.setter
    def config_dir(self, value: Union[str, pathlib.PosixPath]) -> None:
        if type(value) == str:
            value = pathlib.Path(value).expanduser().resolve()
        self._config_dir = value

    @property
    def guacamole_host(self) -> str:
        return self._guacamole_host 

    @guacamole_host.setter
    def guacamole_host(self, value: str) -> None:
        self._guacamole_host = value

    @property
    def guacamole_password(self) -> str:
        return self._guacamole_password 

    @guacamole_password.setter
    def guacamole_password(self, value: str) -> None:
        self._guacamole_password = value

    @property
    def guacamole_username(self) -> str:
        return self._guacamole_host 

    @guacamole_username.setter
    def guacamole_username(self, value: str) -> None:
        self._guacamole_username = value

    @property
    def terraform_dir(self) -> pathlib.PosixPath:
        if self._terraform_dir is None:
            self._terraform_dir = pathliab.Path('~/.config/invocado/terraform').expanduser().resolve()
        if self._terraform_dir:
            self._terraform_dir.mkdir(parents=True, exist_ok=True)
        return self._terraform_dir

    @terraform_dir.setter
    def terraform_dir(self, value: Union[str, pathlib.PosixPath]) -> None:
        if type(value) == str:
            value = pathlib.Path(value).expanduser().resolve()
        self._terraform_dir = value

    @property
    def terraform_repo(self) -> str:
        return self._terraform_repo

    @terraform_repo.setter
    def terraform_repo(self, value: str) -> None:
        self._terraform_repo = value

    @property
    def wol_ip(self) -> str:
        if self._wol_ip is None:
            self._wop_ip = '127.0.0.1'
        return self._wol_ip

    @wol_ip.setter
    def wol_ip(self, value: str) -> None:
        self._wol_ip = value

    @property
    def wol_port(self) -> int:
        if self._wol_port is None:
            self._wol_port = 9
        return self._wol_port

    @wol_port.setter
    def wol_port(self, value: int) -> None:
        self._wol_port = value

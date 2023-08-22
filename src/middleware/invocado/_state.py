import pathlib

from typing import Union


class State(object):
    def __init__(self):
        self._config_dir = None
        self._debug = None
        self._guacamole_authtoken = None
        self._guacamole_datasource = None
        self._guacamole_url = None
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
    def debug(self) -> bool:
        if self._debug is None:
            self._debug = False
        return self._debug

    @debug.setter
    def debug(self, value: bool) -> None:
        self._debug = value

    @property
    def guacamole_authtoken(self) -> str:
        return self._guacamole_authtoken

    @guacamole_authtoken.setter
    def guacamole_authtoken(self, value: str) -> None:
        self._guacamole_authtoken = value

    @property
    def guacamole_datasource(self) -> str:
        return self._guacamole_datasource

    @guacamole_datasource.setter
    def guacamole_datasource(self, value: str) -> str:
        self._guacamole_datasource = value

    @property
    def guacamole_password(self) -> str:
        if self._guacamole_password is None:
            self._guacamole_password = 'guacadmin'
        return self._guacamole_password

    @guacamole_password.setter
    def guacamole_password(self, value: str) -> None:
        self._guacamole_password = value

    @property
    def guacamole_url(self) -> str:
        if self._guacamole_url is None:
            self._guacamole_url = 'http://127.0.0.1:8080/guacamole/'
        return self._guacamole_url

    @guacamole_url.setter
    def guacamole_url(self, value: str) -> None:
        self._guacamole_url = value

    @property
    def guacamole_username(self) -> str:
        if self._guacamole_username is None:
            self._guacamole_username = 'guacadmin'
        return self._guacamole_username

    @guacamole_username.setter
    def guacamole_username(self, value: str) -> None:
        self._guacamole_username = value

    @property
    def terraform_dir(self) -> pathlib.PosixPath:
        if self._terraform_dir is None:
            self._terraform_dir = pathlib.Path('~/.config/invocado/terraform').expanduser().resolve()
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
            self._wol_ip = '127.0.0.1'
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

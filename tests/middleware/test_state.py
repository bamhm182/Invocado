"""test_state.py

Tests for the State class
"""

import os
import sys
import unittest
import pathlib

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../../src/middleware')))

import invocado  # noqa: E402


class StateTestClass(unittest.TestCase):
    def setUp(self):
        self.state = invocado._state.State()

    def test_config_dir(self):
        self.assertEqual(pathlib.PosixPath, type(self.state.config_dir))
        self.assertEqual(pathlib.PosixPath, type(self.state._config_dir))
        default = pathlib.Path('~/.config/invocado').expanduser().resolve()
        self.assertEqual(default, self.state.config_dir)
        self.state.config_dir = '/tmp'
        self.assertEqual(pathlib.PosixPath, type(self.state.config_dir))
        self.assertEqual(pathlib.Path('/tmp').expanduser().resolve(),
                         self.state.config_dir)
        self.assertEqual(pathlib.Path('/tmp').expanduser().resolve(),
                         self.state._config_dir)

    def test_debug(self):
        self.assertEqual(bool, type(self.state.debug))
        self.assertEqual(bool, type(self.state._debug))
        default = False
        self.assertEqual(default, self.state.debug)
        self.state.debug = True
        self.assertEqual(True, self.state.debug)
        self.assertEqual(True, self.state._debug)

    def test_guacamole_authtoken(self):
        self.assertEqual(type(None), type(self.state.guacamole_authtoken))
        self.assertEqual(type(None), type(self.state._guacamole_authtoken))
        default = None
        self.assertEqual(default, self.state.guacamole_authtoken)
        self.state.guacamole_authtoken = 'tacos'
        self.assertEqual('tacos', self.state.guacamole_authtoken)
        self.assertEqual('tacos', self.state._guacamole_authtoken)

    def test_guacamole_datasource(self):
        self.assertEqual(type(None), type(self.state.guacamole_datasource))
        self.assertEqual(type(None), type(self.state._guacamole_datasource))
        default = None
        self.assertEqual(default, self.state.guacamole_datasource)
        self.state.guacamole_datasource = 'tacos'
        self.assertEqual('tacos', self.state.guacamole_datasource)
        self.assertEqual('tacos', self.state._guacamole_datasource)

    def test_guacamole_password(self):
        self.assertEqual(str, type(self.state.guacamole_password))
        self.assertEqual(str, type(self.state._guacamole_password))
        default = 'guacadmin'
        self.assertEqual(default, self.state.guacamole_password)
        self.state.guacamole_password = 'tacos'
        self.assertEqual('tacos', self.state.guacamole_password)
        self.assertEqual('tacos', self.state._guacamole_password)

    def test_guacamole_url(self):
        self.assertEqual(str, type(self.state.guacamole_url))
        self.assertEqual(str, type(self.state._guacamole_url))
        default = 'http://127.0.0.1:8080/guacamole/'
        self.assertEqual(default, self.state.guacamole_url)
        self.state.guacamole_url = 'tacos'
        self.assertEqual('tacos', self.state.guacamole_url)
        self.assertEqual('tacos', self.state._guacamole_url)

    def test_guacamole_username(self):
        self.assertEqual(str, type(self.state.guacamole_username))
        self.assertEqual(str, type(self.state._guacamole_username))
        default = 'guacadmin'
        self.assertEqual(default, self.state.guacamole_username)
        self.state.guacamole_username = 'tacos'
        self.assertEqual('tacos', self.state.guacamole_username)
        self.assertEqual('tacos', self.state._guacamole_username)

    def test_terraform_dir(self):
        self.assertEqual(pathlib.PosixPath, type(self.state.terraform_dir))
        self.assertEqual(pathlib.PosixPath, type(self.state._terraform_dir))
        default = pathlib.Path('~/.config/invocado/terraform').expanduser().resolve()
        self.assertEqual(default, self.state.terraform_dir)
        self.state.terraform_dir = '/tmp'
        self.assertEqual(pathlib.Path('/tmp'), self.state.terraform_dir)
        self.assertEqual(pathlib.Path('/tmp'), self.state._terraform_dir)

    def test_terraform_repo(self):
        self.assertEqual(type(None), type(self.state.terraform_repo))
        self.assertEqual(type(None), type(self.state._terraform_repo))
        default = None
        self.assertEqual(default, self.state.terraform_repo)
        self.state.terraform_repo = 'tacos'
        self.assertEqual('tacos', self.state.terraform_repo)
        self.assertEqual('tacos', self.state._terraform_repo)

    def test_wol_ip(self):
        self.assertEqual(str, type(self.state.wol_ip))
        self.assertEqual(str, type(self.state._wol_ip))
        default = '127.0.0.1'
        self.assertEqual(default, self.state.wol_ip)
        self.state.wol_ip = '8.8.8.8'
        self.assertEqual('8.8.8.8', self.state.wol_ip)
        self.assertEqual('8.8.8.8', self.state._wol_ip)

    def test_wol_port(self):
        self.assertEqual(int, type(self.state.wol_port))
        self.assertEqual(int, type(self.state._wol_port))
        default = 9
        self.assertEqual(default, self.state.wol_port)
        self.state.wol_port = 12345
        self.assertEqual(12345, self.state.wol_port)
        self.assertEqual(12345, self.state._wol_port)

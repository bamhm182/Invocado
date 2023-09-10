"""test_db.py

Tests for the Db class
"""

import os
import pathlib
import sys
import unittest

from unittest.mock import patch, MagicMock, call

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../../src/middleware')))

import invocado  # noqa: E402


class DbTestClass(unittest.TestCase):
    def setUp(self):
        self.state = invocado._state.State()
        self.db = invocado.plugins.Db(self.state, establish_db=MagicMock())
        self.db.utils = MagicMock()
        self.real_establish_db = invocado.plugins.db.Db.establish_db

    def test_add_tf_folders(self):
        self.db.strip_existing_tf_folders = MagicMock()
        folders = [
            {'path': 'test/one'},
            {'path': 'test/two'},
            {'path': 'test/three'},
        ]
        stripped_folders = folders[1:]
        self.db.strip_existing_tf_folders.return_value = stripped_folders
        self.db.add_tf_folders(folders)
        self.db.strip_existing_tf_folders.assert_called_with(folders)
        self.db.session_maker.assert_called()
        self.db.session_maker.return_value.add.assert_called()

    @patch('alembic.config.Config')
    @patch('alembic.command')
    @patch('sqlalchemy.create_engine')
    @patch('sqlalchemy.event')
    @patch('pathlib.Path', return_value=pathlib.Path('/tmp/one/two'))
    def test_establish_db(self, mock_path, mock_event, mock_create_engine, mock_command, mock_config):
        self.state.config_dir = '/tmp'
        self.real_establish_db(self.db)
        mock_config.assert_called_with()
        mock_config.return_value.set_main_option.assert_has_calls([
            call('script_location', '/tmp/db/alembic'),
            call('version_locations', '/tmp/db/alembic/versions'),
            call('sqlalchemy.url', 'sqlite:////tmp/one/two/invocado.db')
        ])
        mock_command.upgrade.assert_called_with(mock_config.return_value, 'head')
        mock_create_engine.assert_called_with('sqlite:////tmp/one/two/invocado.db')
        mock_event.listen.assert_called_with(mock_create_engine.return_value, 'connect', self.db._fk_pragma_on_connect)

    def test_foreign_keys_on(self):
        mock = MagicMock()
        self.db._fk_pragma_on_connect(mock, None)
        mock.execute.assert_called_with('pragma foreign_keys=ON')

    def test_get_config(self):
        config = invocado.db.models.Config(wol_port=12345)
        query = self.db.session_maker.return_value.query
        query.return_value.filter_by.return_value.first.return_value = config

        self.assertEqual(12345, self.db.get_config('wol_port'))

        self.db.session_maker.assert_called_with()
        query.assert_called_with(invocado.db.models.Config)
        query.return_value.filter_by.assert_called_with(id=1)
        query.return_value.filter_by.return_value.first.assert_called_with()
        self.db.session_maker.return_value.close.assert_called_with()

    @patch('invocado.plugins.db.Config')
    def test_get_config_no_config(self, mock_config):
        query = self.db.session_maker.return_value.query
        query.return_value.filter_by.return_value.first.return_value = None
        config = invocado.db.models.config.Config()
        mock_config.return_value = config

        self.assertEqual(None, self.db.get_config('wol_port'))
        mock_config.assert_called_with()
        self.db.session_maker.return_value.add.assert_called_with(config)
        self.db.session_maker.return_value.close.assert_called_with()

    def test_get_mac_mappings_format_1(self):
        self.db.get_config = MagicMock()
        self.db.get_config.return_value = 'FFFFVVVVIIII'
        query = self.db.session_maker.return_value.query
        db_folders = [
            invocado.db.models.TerraformFolder(id=0, path='one'),
            invocado.db.models.TerraformFolder(id=1, path='two'),
            invocado.db.models.TerraformFolder(id=2, path='three/one'),
            invocado.db.models.TerraformFolder(id=10275, path='three/two'),  # id: 0x2823
        ]
        db_vlans = [
            invocado.db.models.TerraformVLAN(id=0, name='myVLAN'),
            invocado.db.models.TerraformVLAN(id=18274, name='myOtherVLAN'),  # id: 0x4762
        ]

        query.return_value.all.side_effect = [
            db_folders,
            db_vlans,
        ]

        expected_outcome = {
            'macs': [
                '00:00:00:00:FF:FF',
                '00:00:47:62:FF:FF',
                '00:01:00:00:FF:FF',
                '00:01:47:62:FF:FF',
                '00:02:00:00:FF:FF',
                '00:02:47:62:FF:FF',
                '28:23:00:00:FF:FF',
                '28:23:47:62:FF:FF',
            ],
            'folders': {
                0: 'one',
                1: 'two',
                2: 'three/one',
                10275: 'three/two',
            },
            'vlans': {
                0: 'myVLAN',
                18274: 'myOtherVLAN',
            },
        }

        actual_outcome = self.db.get_mac_mappings()

        self.assertEqual(len(expected_outcome), len(actual_outcome))
        self.assertEqual(len(expected_outcome.get('macs')), len(actual_outcome.get('macs')))
        self.assertEqual(len(expected_outcome.get('folders')), len(actual_outcome.get('folders')))
        self.assertEqual(len(expected_outcome.get('vlans')), len(actual_outcome.get('vlans')))

        for category in expected_outcome.keys():
            self.assertTrue(category in actual_outcome.keys())
            if type(expected_outcome.get(category)) == list:
                for item in expected_outcome.get(category):
                    self.assertTrue(item in actual_outcome.get(category))
            elif type(expected_outcome.get(category)) == dict:
                for key in expected_outcome.get(category, dict()).keys():
                    self.assertTrue(key in actual_outcome.get(category, dict()).keys())
                    self.assertEqual(expected_outcome.get(category, dict()).get(key),
                                     actual_outcome.get(category, dict()).get(key))

        self.db.session_maker.assert_called_with()
        query.assert_has_calls([
            call(invocado.db.models.TerraformFolder),
            call().all(),
            call(invocado.db.models.TerraformVLAN),
            call().all(),
        ])
        self.db.session_maker.return_value.close.assert_called_with()

    def test_get_mac_mappings_format_2(self):
        self.db.get_config = MagicMock()
        self.db.get_config.return_value = 'VVFFFFFFFFII'
        query = self.db.session_maker.return_value.query
        db_folders = [
            invocado.db.models.TerraformFolder(id=0, path='one'),
            invocado.db.models.TerraformFolder(id=730480392, path='two'),  # id: 0x2B8A3F08
        ]
        db_vlans = [
            invocado.db.models.TerraformVLAN(id=0, name='myVLAN'),
            invocado.db.models.TerraformVLAN(id=67, name='myOtherVLAN'),  # id: 0x43
        ]

        query.return_value.all.side_effect = [
            db_folders,
            db_vlans,
        ]

        expected_outcome = {
            'macs': [
                '00:00:00:00:00:FF',
                '43:00:00:00:00:FF',
                '00:2B:8A:3F:08:FF',
                '43:2B:8A:3F:08:FF',
            ],
            'folders': {
                0: 'one',
                730480392: 'two',
            },
            'vlans': {
                0: 'myVLAN',
                67: 'myOtherVLAN',
            }
        }

        actual_outcome = self.db.get_mac_mappings()

        self.assertEqual(len(expected_outcome), len(actual_outcome))
        self.assertEqual(len(expected_outcome.get('macs')), len(actual_outcome.get('macs')))
        self.assertEqual(len(expected_outcome.get('folders')), len(actual_outcome.get('folders')))
        self.assertEqual(len(expected_outcome.get('vlans')), len(actual_outcome.get('vlans')))

        for category in expected_outcome.keys():
            self.assertTrue(category in actual_outcome.keys())
            if type(expected_outcome.get(category)) == list:
                for item in expected_outcome.get(category):
                    self.assertTrue(item in actual_outcome.get(category))
            elif type(expected_outcome.get(category)) == dict:
                for key in expected_outcome.get(category, dict()).keys():
                    self.assertTrue(key in actual_outcome.get(category, dict()).keys())
                    self.assertEqual(expected_outcome.get(category, dict()).get(key),
                                     actual_outcome.get(category, dict()).get(key))

        self.db.session_maker.assert_called_with()
        query.assert_has_calls([
            call(invocado.db.models.TerraformFolder),
            call().all(),
            call(invocado.db.models.TerraformVLAN),
            call().all(),
        ])
        self.db.session_maker.return_value.close.assert_called_with()

    def test_get_mac_mappings_no_vlans(self):
        """
        If no VLANs exist, a Default one is thrown into this.
        The creation functionality will not try to add a VLAN if it's invalid
        """
        self.db.get_config = MagicMock()
        self.db.get_config.return_value = 'VVFFFFFFFFII'
        query = self.db.session_maker.return_value.query
        db_folders = [
            invocado.db.models.TerraformFolder(id=0, path='one'),
            invocado.db.models.TerraformFolder(id=730480392, path='two'),  # id: 0x2B8A3F08
        ]
        db_vlans = [
        ]

        query.return_value.all.side_effect = [
            db_folders,
            db_vlans,
        ]

        expected_outcome = {
            'macs': [
                'FF:00:00:00:00:FF',
                'FF:2B:8A:3F:08:FF',
            ],
            'folders': {
                0: 'one',
                730480392: 'two',
            },
            'vlans': {
                255: 'Default',
            },
        }

        actual_outcome = self.db.get_mac_mappings()

        self.assertEqual(len(expected_outcome), len(actual_outcome))
        self.assertEqual(len(expected_outcome.get('macs')), len(actual_outcome.get('macs')))
        self.assertEqual(len(expected_outcome.get('folders')), len(actual_outcome.get('folders')))
        self.assertEqual(len(expected_outcome.get('vlans')), len(actual_outcome.get('vlans')))

        for category in expected_outcome.keys():
            self.assertTrue(category in actual_outcome.keys())
            if type(expected_outcome.get(category)) == list:
                for item in expected_outcome.get(category):
                    self.assertTrue(item in actual_outcome.get(category))
            elif type(expected_outcome.get(category)) == dict:
                for key in expected_outcome.get(category, dict()).keys():
                    self.assertTrue(key in actual_outcome.get(category, dict()).keys())
                    self.assertEqual(expected_outcome.get(category, dict()).get(key),
                                     actual_outcome.get(category, dict()).get(key))

        self.db.session_maker.assert_called_with()
        query.assert_has_calls([
            call(invocado.db.models.TerraformFolder),
            call().all(),
            call(invocado.db.models.TerraformVLAN),
            call().all(),
        ])
        self.db.session_maker.return_value.close.assert_called_with()

    def test_get_mac_mappings_no_vlans_2(self):
        """
        If no VLANs exist, a Default one is thrown into this.
        The creation functionality will not try to add a VLAN if it's invalid
        """
        self.db.get_config = MagicMock()
        self.db.get_config.return_value = 'VVVVVVFFFFII'
        query = self.db.session_maker.return_value.query
        db_folders = [
            invocado.db.models.TerraformFolder(id=0, path='one'),
            invocado.db.models.TerraformFolder(id=10, path='two'),  # id: 0x0A
        ]
        db_vlans = [
        ]

        query.return_value.all.side_effect = [
            db_folders,
            db_vlans,
        ]

        expected_outcome = {
            'macs': [
                'FF:FF:FF:00:00:FF',
                'FF:FF:FF:00:0A:FF',
            ],
            'folders': {
                0: 'one',
                10: 'two',
            },
            'vlans': {
                16777215: 'Default',
            },
        }

        actual_outcome = self.db.get_mac_mappings()

        self.assertEqual(len(expected_outcome), len(actual_outcome))
        self.assertEqual(len(expected_outcome.get('macs')), len(actual_outcome.get('macs')))
        self.assertEqual(len(expected_outcome.get('folders')), len(actual_outcome.get('folders')))
        self.assertEqual(len(expected_outcome.get('vlans')), len(actual_outcome.get('vlans')))

        for category in expected_outcome.keys():
            self.assertTrue(category in actual_outcome.keys())
            if type(expected_outcome.get(category)) == list:
                for item in expected_outcome.get(category):
                    self.assertTrue(item in actual_outcome.get(category))
            elif type(expected_outcome.get(category)) == dict:
                for key in expected_outcome.get(category, dict()).keys():
                    self.assertTrue(key in actual_outcome.get(category, dict()).keys())
                    self.assertEqual(expected_outcome.get(category, dict()).get(key),
                                     actual_outcome.get(category, dict()).get(key))

        self.db.session_maker.assert_called_with()
        query.assert_has_calls([
            call(invocado.db.models.TerraformFolder),
            call().all(),
            call(invocado.db.models.TerraformVLAN),
            call().all(),
        ])
        self.db.session_maker.return_value.close.assert_called_with()

    def test_guacamole_authtoken(self):
        self.state.guacamole_authtoken = '12345'
        self.assertEqual('12345', self.db.guacamole_authtoken)
        self.db.guacamole_authtoken = '54321'
        self.assertEqual('54321', self.state.guacamole_authtoken)

    def test_guacamole_datasource(self):
        self.state.guacamole_datasource = '12345'
        self.assertEqual('12345', self.db.guacamole_datasource)
        self.db.guacamole_datasource = '54321'
        self.assertEqual('54321', self.state.guacamole_datasource)

    def test_guacamole_password_getter(self):
        self.db.get_config = MagicMock()
        self.db.get_config.return_value = '12345'
        self.db.state = MagicMock()

        self.db.state.guacamole_password = None
        self.assertTrue('12345', self.db.guacamole_password)

        self.db.state.guacamole_password = '54321'
        self.assertTrue('54321', self.db.guacamole_password)

        self.db.get_config.assert_has_calls([call('guacamole_password')])

    def test_guacamole_password_setter(self):
        self.db.set_config = MagicMock()

        self.db.guacamole_password = 'tacobell'
        self.db.set_config.assert_called_with('guacamole_password', 'tacobell')
        self.assertEqual(self.state.guacamole_password, 'tacobell')

    def test_guacamole_url_getter(self):
        self.db.get_config = MagicMock()
        self.db.get_config.return_value = '12345'
        self.db.state = MagicMock()

        self.db.state.guacamole_url = None
        self.assertTrue('12345', self.db.guacamole_url)

        self.db.state.guacamole_url = '54321'
        self.assertTrue('54321', self.db.guacamole_url)

        self.db.get_config.assert_has_calls([call('guacamole_url')])

    def test_guacamole_url_setter(self):
        self.db.set_config = MagicMock()

        self.db.guacamole_url = 'tacobell'
        self.db.set_config.assert_called_with('guacamole_url', 'tacobell')
        self.assertEqual(self.state.guacamole_url, 'tacobell')

    def test_guacamole_username_getter(self):
        self.db.get_config = MagicMock()
        self.db.get_config.return_value = '12345'
        self.db.state = MagicMock()

        self.db.state.guacamole_username = None
        self.assertTrue('12345', self.db.guacamole_username)

        self.db.state.guacamole_username = '54321'
        self.assertTrue('54321', self.db.guacamole_username)

        self.db.get_config.assert_has_calls([call('guacamole_username')])

    def test_guacamole_username_setter(self):
        self.db.set_config = MagicMock()

        self.db.guacamole_username = 'tacobell'
        self.db.set_config.assert_called_with('guacamole_username', 'tacobell')
        self.assertEqual(self.state.guacamole_username, 'tacobell')

    @patch('builtins.print')
    @patch('invocado.plugins.db.tabulate')
    def test_print_mac_mappings(self, mock_tabulate, mock_print):
        mock_tabulate.return_value = 'tabulate_output'
        self.db.get_config = MagicMock()
        self.db.get_config.return_value = 'FFFFVVVVIIII'
        self.db.get_mac_mappings = MagicMock()
        self.db.get_mac_mappings.return_value = {
            'macs': [
                '00:11:22:33:44:55',
                '00:00:00:00:00:00',
                'AA:BB:CC:DD:EE:FF',
            ],
            'folders': {
                0: 'one',
                1: 'zebras',
                2: 'apples',
            },
            'vlans': {
                0: 'myVLAN',
                1: 'myOtherVLAN',
                2: 'anotherVLAN',
            }
        }

        self.db.utils.decode_mac.side_effect = [
            {
                'mac': '00:11:22:33:44:55',
                'vlan': 0,
                'folder': 1,
            },
            {
                'mac': '00:00:00:00:00:00',
                'vlan': 1,
                'folder': 0,
            },
            {
                'mac': 'AA:BB:CC:DD:EE:FF',
                'vlan': 2,
                'folder': 2,
            }
        ]

        expected_data = [
                ['00:00:00:00:00:00', 'myOtherVLAN (1)', 'one (0)'],
                ['00:11:22:33:44:55', 'myVLAN (0)', 'zebras (1)'],
                ['AA:BB:CC:DD:EE:FF', 'anotherVLAN (2)', 'apples (2)'],
        ]

        self.db.print_mac_mappings()

        mock_tabulate.assert_called_with(expected_data, headers=['MAC', 'VLAN', 'Terraform Folder'])
        mock_print.assert_called_with('tabulate_output')

    @patch('pathlib.Path')
    def test_prune_terraform_folders(self, mock_path):
        folders = [
            invocado.db.models.TerraformFolder(path='one'),
            invocado.db.models.TerraformFolder(path='two'),
            invocado.db.models.TerraformFolder(path='three'),
            invocado.db.models.TerraformFolder(path='four'),
            invocado.db.models.TerraformFolder(path='five'),
        ]

        self.db.terraform_dir = '/tmp/terraform'
        query = self.db.session_maker.return_value.query
        query.return_value.all.return_value = folders
        mock_path.return_value.__truediv__.return_value.__truediv__.return_value.exists.side_effect = [
            True,
            False,
            True,
            False,
            False,
        ]

        self.db.prune_terraform_folders()

        self.db.session_maker.return_value.delete.assert_has_calls([
            call(folders[1]),
            call(folders[3]),
            call(folders[4]),
        ])
        self.db.session_maker.return_value.commit.assert_called_with()
        self.db.session_maker.return_value.close.assert_called_with()

    def test_set_config(self):
        config = invocado.db.models.Config()
        invocado.plugins.db.Config = MagicMock()
        query = self.db.session_maker.return_value.query
        query.return_value.filter_by.return_value.first.return_value = config

        self.db.set_config('wol_ip', 'testingvalue')
        self.db.session_maker.return_value.commit.assert_called_with()
        self.db.session_maker.return_value.close.assert_called_with()

    @patch('invocado.plugins.db.Config')
    def test_set_config_no_config(self, mock_config):
        config = invocado.db.models.Config()
        query = self.db.session_maker.return_value.query
        query.return_value.filter_by.return_value.first.return_value = None
        mock_config.return_value = config

        self.db.set_config('tacos', 'tasty')
        mock_config.assert_called_with()
        self.assertTrue(hasattr(config, 'tacos'))
        self.assertEqual(config.tacos, 'tasty')
        self.db.session_maker.return_value.add.assert_called_with(config)
        self.db.session_maker.return_value.commit.assert_called_with()
        self.db.session_maker.return_value.close.assert_called_with()

    def test_strip_existing_tf_folders(self):
        folders = [
            {'path': 'one'},
            {'path': 'two'},
            {'path': 'three/one'},
            {'path': 'three/two'},
        ]
        query = self.db.session_maker.return_value.query
        query.return_value.filter_by.return_value.first.side_effect = [
            True,
            False,
            False,
            True,
        ]

        self.assertEqual([folders[1], folders[2]], self.db.strip_existing_tf_folders(folders))

        self.db.session_maker.assert_called_with()
        query.assert_called_with(invocado.db.models.TerraformFolder)
        query.return_value.filter_by.assert_has_calls([])
        query.return_value.filter_by.first.assert_has_calls([])
        self.db.session_maker.return_value.close.assert_called_with()

    def test_terraform_dir_getter(self):
        self.db.get_config = MagicMock()
        self.db.get_config.return_value = '12345'
        self.db.state = MagicMock()

        self.db.state.terraform_dir = None
        self.assertTrue('12345', self.db.terraform_dir)

        self.db.state.terraform_dir = '54321'
        self.assertTrue('54321', self.db.terraform_dir)

        self.db.get_config.assert_has_calls([call('terraform_dir')])

    def test_terraform_dir_setter(self):
        self.db.set_config = MagicMock()

        self.db.terraform_dir = '/tmp/terraform'
        self.db.set_config.assert_called_with('terraform_dir', '/tmp/terraform')
        self.assertEqual(self.state.terraform_dir, pathlib.Path('/tmp/terraform'))

    def test_terraform_repo_getter(self):
        self.db.get_config = MagicMock()
        self.db.get_config.return_value = '12345'
        self.db.state = MagicMock()

        self.db.state.terraform_repo = None
        self.assertTrue('12345', self.db.terraform_repo)

        self.db.state.terraform_repo = '54321'
        self.assertTrue('54321', self.db.terraform_repo)

        self.db.get_config.assert_has_calls([call('terraform_repo')])

    def test_terraform_repo_setter(self):
        self.db.set_config = MagicMock()

        self.db.terraform_repo = 'https://github.com/someone/something.git'
        self.db.set_config.assert_called_with('terraform_repo', 'https://github.com/someone/something.git')
        self.assertEqual(self.state.terraform_repo, 'https://github.com/someone/something.git')

    def test_wol_ip_getter(self):
        self.db.get_config = MagicMock()
        self.db.get_config.return_value = '127.0.0.1'
        self.db.state = MagicMock()

        self.db.state.wol_ip = None
        self.assertTrue('127.0.0.1', self.db.wol_ip)

        self.db.state.wol_ip = '192.168.10.10'
        self.assertTrue('192.168.10.10', self.db.wol_ip)

        self.db.get_config.assert_has_calls([call('wol_ip')])

    def test_wol_ip_setter(self):
        self.db.set_config = MagicMock()

        self.db.wol_ip = '86.75.30.9'
        self.db.set_config.assert_called_with('wol_ip', '86.75.30.9')
        self.assertEqual(self.state.wol_ip, '86.75.30.9')

    def test_wol_mac_mapping_getter(self):
        self.db.get_config = MagicMock()
        self.db.get_config.return_value = 'FFFFVVVVIIII'
        self.assertEqual('FFFFVVVVIIII', self.db.wol_mac_mapping)

    def test_wol_mac_mapping_setter(self):
        self.db.set_config = MagicMock()

        self.db.wol_mac_mapping = 'FFFFVVVVIIII'  # Valid
        self.db.wol_mac_mapping = 'MAHWMAKSHSJA'  # Prevent Invalid Characters
        self.db.wol_mac_mapping = 'FFFFFFFFFFII'  # Valid
        self.db.wol_mac_mapping = 'FIFIFIFIFIFI'  # Prevent Non-Grouped Characters

        self.db.set_config.assert_has_calls([
            call('wol_mac_mapping', 'FFFFVVVVIIII'),
            call('wol_mac_mapping', 'FFFFFFFFFFII')
        ])

    def test_wol_port_getter(self):
        self.db.get_config = MagicMock()
        self.db.get_config.return_value = '12345'
        self.db.state = MagicMock()

        self.db.state.wol_port = None
        self.assertTrue('12345', self.db.wol_port)

        self.db.state.wol_port = '54321'
        self.assertTrue('54321', self.db.wol_port)

        self.db.get_config.assert_has_calls([call('wol_port')])

    def test_wol_port_setter(self):
        self.db.set_config = MagicMock()

        self.db.wol_port = '12345'
        self.db.set_config.assert_called_with('wol_port', 12345)
        self.assertEqual(self.state.wol_port, 12345)

"""test_guacamole.py

Tests for the Guacamole class
"""

import os
import sys
import unittest

from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../../src/middleware')))

import invocado  # noqa: E402


class GuacamoleTestClass(unittest.TestCase):
    def setUp(self):
        self.state = invocado._state.State()
        self.guacamole = invocado.plugins.Guacamole(self.state, session=MagicMock())
        self.guacamole.db = MagicMock()
        self.guacamole.debug = MagicMock()
        self.real_guacamole_request = invocado.plugins.guacamole.Guacamole.request
        self.guacamole.request = MagicMock()

    @patch('json.loads')
    def test_authenticate(self, mock_json_loads):
        self.guacamole.db.guacamole_username = 'guacuser'
        self.guacamole.db.guacamole_password = 'guacuser'
        content = {
            'authToken': '12345',
            'dataSource': 'mySQL',
        }

        mock_json_loads.return_value = content

        self.guacamole.request.return_value.status_code = 200
        self.guacamole.request.return_value.content = content

        self.guacamole.authenticate()

        mock_json_loads.assert_called_with(content)
        self.guacamole.request.assert_called_with('tokens', 'POST',
                                                  data={'username': 'guacuser', 'password': 'guacuser'})
        self.guacamole.session.headers.update.assert_called_with({'guacamole-token': '12345'})
        self.guacamole.db.guacamole_authtoken = '12345'
        self.guacamole.db.guacamole_datasource = 'mySQL'

    def test_authenticate_bad_creds(self):
        self.guacamole.request.return_value.status_code = 403

        self.guacamole.authenticate()

        self.guacamole.debug.log.assert_called_with('Authentication Failure',
                                                    'Invocado failed to log in with provided credentials')

    @patch('json.loads')
    def test_get_connection_parameters(self, mock_json_loads):
        self.guacamole.state.guacamole_datasource = 'pizza'
        self.guacamole.request.return_value.status_code = 200
        mock_json_loads.return_value = 'json_ret'
        self.assertEqual('json_ret', self.guacamole.get_connection_parameters('noneya'))
        self.guacamole.request.assert_called_with('session/data/pizza/connections/noneya/parameters')

    @patch('json.loads')
    def test_get_connections(self, mock_json_loads):
        self.guacamole.state.guacamole_datasource = 'pizza'
        self.guacamole.request.return_value.status_code = 200
        mock_json_loads.return_value = 'json_ret'
        self.assertEqual('json_ret', self.guacamole.get_connections())
        self.guacamole.request.assert_called_with('session/data/pizza/connections')

    def test_request(self):
        self.guacamole.session.request.return_value.status_code = 200
        self.guacamole.session.request.return_value.content = b'Something something dark side'
        self.guacamole.db.guacamole_url = 'http://guac/'
        self.assertEqual(self.guacamole.session.request.return_value,
                         self.real_guacamole_request(self.guacamole, 'my_endpoint'))
        self.guacamole.session.request.assert_called_with('GET', 'http://guac/api/my_endpoint')
        self.guacamole.debug.log.assert_called_with('Guacamole API Call',
                                                    '200 -- GET -- http://guac/api/my_endpoint' +
                                                    '\n\tContent: Something something dark side')

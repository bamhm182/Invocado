import json
import requests

from .base import Plugin


class Guacamole(Plugin):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for plugin in ['Db', 'Debug']:
            setattr(self,
                    plugin.lower(),
                    self.registry.get(plugin)(self.state))

        self.session = kwargs.get('session', requests.session)()

    def authenticate(self):
        data = {
            'username': self.db.guacamole_username,
            'password': self.db.guacamole_password
        }
        ret = self.request('tokens', 'POST', data=data)
        if ret.status_code == 200:
            j = json.loads(ret.content)
            self.state.guacamole_authtoken = j.get('authToken')
            self.session.headers.update({'guacamole-token': j.get('authToken')})
            self.state.guacamole_datasource = j.get('dataSource')
        elif ret.status_code == 403:
            self.debug.log('Authentication Failure', 'Invocado failed to log in with provided credentials')

    def find_connection(self, **kwargs):
        pass

    def get_connection_parameters(self, connection):
        ret = self.request(f'session/data/{self.state.guacamole_datasource}/connections/{connection}/parameters')
        if ret.status_code == 200:
            return json.loads(ret.content)

    def get_connections(self):
        ret = self.request(f'session/data/{self.state.guacamole_datasource}/connections')
        if ret.status_code == 200:
            return json.loads(ret.content)

    def request(self, endpoint: str, method: str = 'GET', **kwargs):
        method = method.upper()
        response = self.session.request(method, f'{self.db.guacamole_url}api/{endpoint}', **kwargs)
        self.debug.log('Guacamole API Call',
                       f'{response.status_code} -- {method} -- {self.db.guacamole_url}api/{endpoint}' +
                       f'\n\tContent: {response.content.decode()}')
        return response

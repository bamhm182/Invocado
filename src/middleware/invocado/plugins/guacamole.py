import json
import requests

from .base import Plugin


class Guacamole(Plugin):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for plugin in ['Db']:
            setattr(self,
                    plugin.lower(),
                    self.registry.get(plugin)(self.state))

        self.session = requests.session()

    def find_connection(self, **kwargs):
        pass

    def get_connections(self):
        ret = self.request(f'session/data/{self.state.guacamole_datasource}/connections')
        if ret.status_code == 200:
            return json.loads(ret.content)

    def get_connection_parameters(self, connection):
        ret = self.request(f'session/data/{self.state.guacamole_datasource}/connections/{connection}/parameters')
        if ret.status_code == 200:
            return json.loads(ret.content)

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
            print('Guacamole credentials appear to be incorrect...')

    def request(self, endpoint:str, method:str='GET', **kwargs):
        print(f'{self.db.guacamole_url}api/{endpoint}')
        return self.session.request(method, f'{self.db.guacamole_url}api/{endpoint}', **kwargs)

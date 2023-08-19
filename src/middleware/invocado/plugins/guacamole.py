import socket

from .base import Plugin


class Guacamole(Plugin):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for plugin in ['Db']:
            setattr(self,
                    plugin.lower(),
                    self.registry.get(plugin)(self.state))

    def start_wol_listener(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(self.db.wol_ip)
        print(self.db.wol_port)
        sock.bind((self.db.wol_ip, self.db.wol_port))


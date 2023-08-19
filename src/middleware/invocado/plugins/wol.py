"""
invocado.plugins.wol

Implements functionality to take commands from Guacamole's Wake-on-LAN functionality
"""
import socket

from .base import Plugin
from multiprocessing import Process


class Wol(Plugin):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for plugin in ['Db']:
            setattr(self,
                    plugin.lower(),
                    self.registry.get(plugin)(self.state))

    def start_listener(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.db.wol_ip, self.db.wol_port))

        while True:
            data, addr = sock.recvfrom(108)
            p = Process(target=self.handle_packet, args=(data,))
            p.start()

    def handle_packet(self, data):
        payload = binascii.hexlify(data)
        DGRAM_REGEX = re.compile(br'(?:^([fF]{12})(([0-9a-fA-F]{12}){16})([0-9a-fA-F]{12})?$)')

        if DGRAM_REGEX.match(payload):
            search = DGRAM_REGEX.search(payload)

            mac = search.group(3)
            password = search.group(4)

            definition = self.parse_mac(mac)
            if definition:
                definition = self.tf.create(definition)
                self.guac.update_connection(definition)

                if definition.get('protocol') == 'rdp':
                    self.tf.get_ip(definition)
                    if definition['ip']:
                        self.guac.update_connection(definition)
                elif definition.get('protocol') == 'vnc':
                    self.tf.get_vnc_port(definition)
                    if definition['port']:
                        self.guac.update_connection(definition)




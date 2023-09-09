"""invocado.plugins.wol

Implements functionality to take commands from Guacamole's Wake-on-LAN functionality
"""
import binascii
import re

from .base import Plugin


class Wol(Plugin):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for plugin in ['Db', 'Utils']:
            setattr(self,
                    plugin.lower(),
                    self.registry.get(plugin)(self.state))

    def handle_packet(self, data: bytes) -> dict:
        if type(data) == tuple:
            payload = binascii.hexlify(data[0]).decode()
        elif type(data) == bytes:
            payload = binascii.hexlify(data).decode()
        else:
            payload = data
        DGRAM_REGEX = re.compile(r'(?:^([fF]{12})(([0-9a-fA-F]{12}){16})([0-9a-fA-F]{12})?$)')

        if DGRAM_REGEX.match(payload):
            search = DGRAM_REGEX.search(payload)

            mac = search.group(3)
            self.debug.log('WOL Packet Recieved', mac)

            definition = self.utils.decode_mac(mac)
            self.debug.log('WOL MAC Decoded', definition)

"""invocado.plugins.wol

Implements functionality to take commands from Guacamole's Wake-on-LAN functionality
"""
import binascii
import re

from .base import Plugin


class Wol(Plugin):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for plugin in ['Db']:
            setattr(self,
                    plugin.lower(),
                    self.registry.get(plugin)(self.state))

    def decode_mac(self, mac: str) -> dict:
        mac = self.validate_mac(mac)

        if mac:
            definition = {
                'mac': ':'.join([mac[i:i+2] for i in range(0, len(mac), 2)])
            }

            folder = ''
            instance = ''
            vlan = ''

            for i, val in enumerate(self.db.wol_mac_mapping):
                if val == 'F':
                    folder += mac[i]
                elif val == 'V':
                    vlan += mac[i]
                elif val == 'I':
                    instance += mac[i]

            if folder:
                definition['folder'] = int(folder, 16)
            if vlan:
                definition['vlan'] = int(vlan, 16)
            if instance:
                definition['instance'] = int(instance, 16)

            return definition

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

            definition = self.db.decode_mac(mac)
            self.debug.log('WOL MAC Decoded', definition)

    def validate_mac(self, mac: str) -> str:
        if type(mac) == bytes:
            mac = mac.decode()
        mac = re.sub(r'[^0-9a-fA-F]', '', mac)
        if len(mac) == 12:
            return mac.upper()

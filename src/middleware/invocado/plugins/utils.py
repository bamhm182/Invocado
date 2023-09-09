"""invocado.plugins.utils

Implements Utilities which may be used across other plugins
"""
import re

from .base import Plugin


class Utils(Plugin):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def decode_mac(self, mac: str, wol_mac_mapping: str) -> dict:
        mac = self.validate_mac(mac)

        if mac:
            definition = {
                'mac': ':'.join([mac[i:i+2] for i in range(0, len(mac), 2)])
            }

            folder = ''
            instance = ''
            vlan = ''

            for i, val in enumerate(wol_mac_mapping):
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

    def validate_mac(self, mac: str) -> str:
        if type(mac) == bytes:
            mac = mac.decode()
        mac = re.sub(r'[^0-9a-fA-F]', '', mac)
        if len(mac) == 12:
            return mac.upper()

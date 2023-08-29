"""test_wol.py

Tests for the Wol class
"""

import os
import sys
import unittest

from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../../src/middleware')))

import invocado  # noqa: E402


class StateTestClass(unittest.TestCase):
    def setUp(self):
        self.state = invocado._state.State()
        self.wol = invocado.plugins.Wol(self.state)
        self.wol.db = MagicMock()
        self.wol.debug = MagicMock()

    def test_decode_mac(self):
        mac = '000102:03:0405'
        self.wol.validate_mac = MagicMock()
        self.wol.validate_mac.return_value = '000102030405'
        self.wol.db.wol_mac_mapping = 'FFFFFFVVIIII'
        expected = {
            'folder': 258,
            'instance': 1029,
            'mac': '00:01:02:03:04:05',
            'vlan': 3,
        }
        self.assertEqual(expected, self.wol.decode_mac(mac))

    def test_decode_mac_two(self):
        mac = '0001:0203:0405'
        self.wol.validate_mac = MagicMock()
        self.wol.validate_mac.return_value = '000102030405'
        self.wol.db.wol_mac_mapping = 'FFFFVVVVIIII'
        expected = {
            'folder': 1,
            'instance': 1029,
            'mac': '00:01:02:03:04:05',
            'vlan': 515,
        }
        self.assertEqual(expected, self.wol.decode_mac(mac))

    def test_decode_mac_why(self):
        mac = '00:01:02:03:04:05'
        self.wol.validate_mac = MagicMock()
        self.wol.validate_mac.return_value = '000102030405'
        self.wol.db.wol_mac_mapping = 'FIVVIFVIFIVI'
        expected = {
            'folder': 32,
            'instance': 837,
            'mac': '00:01:02:03:04:05',
            'vlan': 256,
        }
        self.assertEqual(expected, self.wol.decode_mac(mac))

    def test_handle_packet_packet(self):
        data = b'\xFF'*6 + b'\x00\x01\x02\x03\x04\x05'*16
        self.wol.db.decode_mac.return_value = 7
        self.wol.handle_packet(data)
        self.wol.debug.log.assert_has_calls([
            unittest.mock.call('WOL Packet Recieved', '000102030405'),
            unittest.mock.call('WOL MAC Decoded', 7)
        ])
        self.wol.db.decode_mac.assert_called_with('000102030405')

    def test_handle_packet_string(self):
        data = 'F'*12 + '000102030405'*16
        self.wol.db.decode_mac.return_value = 7
        self.wol.handle_packet(data)
        self.wol.debug.log.assert_has_calls([
            unittest.mock.call('WOL Packet Recieved', '000102030405'),
            unittest.mock.call('WOL MAC Decoded', 7)
        ])
        self.wol.db.decode_mac.assert_called_with('000102030405')

    def test_handle_packet_tuple(self):
        data = (b'\xFF'*6 + b'\x00\x01\x02\x03\x04\x05'*16, ('127.0.0.1', 43486))
        self.wol.db.decode_mac.return_value = 7
        self.wol.handle_packet(data)
        self.wol.debug.log.assert_has_calls([
            unittest.mock.call('WOL Packet Recieved', '000102030405'),
            unittest.mock.call('WOL MAC Decoded', 7)
        ])
        self.wol.db.decode_mac.assert_called_with('000102030405')

    def test_validate_mac(self):
        self.assertEqual('0123456789AB', self.wol.validate_mac('01:23:45:67:89:AB'))
        self.assertEqual('0123456789AB', self.wol.validate_mac(b'01:23:45:67:89:AB'))
        self.assertEqual(None, self.wol.validate_mac('This isnt a mac...'))

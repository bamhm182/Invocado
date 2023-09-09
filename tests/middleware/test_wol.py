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
        self.wol.utils = MagicMock()

    def test_handle_packet_packet(self):
        data = b'\xFF'*6 + b'\x00\x01\x02\x03\x04\x05'*16
        self.wol.utils.decode_mac.return_value = 7
        self.wol.handle_packet(data)
        self.wol.debug.log.assert_has_calls([
            unittest.mock.call('WOL Packet Recieved', '000102030405'),
            unittest.mock.call('WOL MAC Decoded', 7)
        ])
        self.wol.utils.decode_mac.assert_called_with('000102030405')

    def test_handle_packet_string(self):
        data = 'F'*12 + '000102030405'*16
        self.wol.utils.decode_mac.return_value = 7
        self.wol.handle_packet(data)
        self.wol.debug.log.assert_has_calls([
            unittest.mock.call('WOL Packet Recieved', '000102030405'),
            unittest.mock.call('WOL MAC Decoded', 7)
        ])
        self.wol.utils.decode_mac.assert_called_with('000102030405')

    def test_handle_packet_tuple(self):
        data = (b'\xFF'*6 + b'\x00\x01\x02\x03\x04\x05'*16, ('127.0.0.1', 43486))
        self.wol.utils.decode_mac.return_value = 7
        self.wol.handle_packet(data)
        self.wol.debug.log.assert_has_calls([
            unittest.mock.call('WOL Packet Recieved', '000102030405'),
            unittest.mock.call('WOL MAC Decoded', 7)
        ])
        self.wol.utils.decode_mac.assert_called_with('000102030405')

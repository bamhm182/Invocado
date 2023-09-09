"""test_utils.py

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
        self.utils = invocado.plugins.Utils(self.state)

    def test_decode_mac(self):
        mac = '000102:03:0405'
        self.utils.validate_mac = MagicMock()
        self.utils.validate_mac.return_value = '000102030405'
        wol_mac_mapping = 'FFFFFFVVIIII'
        expected = {
            'folder': 258,
            'instance': 1029,
            'mac': '00:01:02:03:04:05',
            'vlan': 3,
        }
        self.assertEqual(expected, self.utils.decode_mac(mac, wol_mac_mapping))

    def test_decode_mac_two(self):
        mac = '0001:0203:0405'
        self.utils.validate_mac = MagicMock()
        self.utils.validate_mac.return_value = '000102030405'
        wol_mac_mapping = 'FFFFVVVVIIII'
        expected = {
            'folder': 1,
            'instance': 1029,
            'mac': '00:01:02:03:04:05',
            'vlan': 515,
        }
        self.assertEqual(expected, self.utils.decode_mac(mac, wol_mac_mapping))

    def test_decode_mac_why(self):
        mac = '00:01:02:03:04:05'
        self.utils.validate_mac = MagicMock()
        self.utils.validate_mac.return_value = '000102030405'
        wol_mac_mapping = 'FIVVIFVIFIVI'
        expected = {
            'folder': 32,
            'instance': 837,
            'mac': '00:01:02:03:04:05',
            'vlan': 256,
        }
        self.assertEqual(expected, self.utils.decode_mac(mac, wol_mac_mapping))

    def test_validate_mac(self):
        self.assertEqual('0123456789AB', self.utils.validate_mac('01:23:45:67:89:AB'))
        self.assertEqual('0123456789AB', self.utils.validate_mac(b'01:23:45:67:89:AB'))
        self.assertEqual(None, self.utils.validate_mac('This isnt a mac...'))

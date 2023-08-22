"""test_wol.py

Tests for the Wol class
"""

import os
import sys
import unittest

from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../../src/middleware')))

import invocado  # noqa: E402


class StateTestClass(unittest.TestCase):
    def setUp(self):
        self.state = invocado._state.State()
        self.wol = invocado.plugins.Wol(self.state)
        self.wol.db = MagicMock()

    def test_start_listener(self):
        with patch('socket.socket') as mock_socket:
            mock_socket.return_value.recvfrom.return_value = ('abc', '127.0.0.1')
            # self.wol.start_listener()

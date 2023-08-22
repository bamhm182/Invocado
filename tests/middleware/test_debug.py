"""test_debug.py

Tests for the Debug class
"""

import datetime
import os
import sys
import unittest

from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../../src/middleware')))

import invocado  # noqa: E402


class StateTestClass(unittest.TestCase):
    def setUp(self):
        self.state = invocado._state.State()
        self.debug = invocado.plugins.Debug(self.state)

    def test_log_disabled(self):
        self.state.debug = False
        with patch('builtins.print') as mock_print:
            self.debug.log('title', 'message')
            mock_print.assert_not_called()

    def test_log_enabled(self):
        self.state.debug = True
        with patch('builtins.print') as mock_print:
            now = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
            self.debug.log('title', 'message')
            mock_print.assert_called_with(f'{now} -- TITLE\n\tmessage')

"""test_handler.py

Tests for the Handler class
"""

import os
import sys
import unittest

from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../../src/middleware')))

import invocado  # noqa: E402


class HandlerTestClass(unittest.TestCase):
    def setUp(self):
        for plugin in invocado.plugins.base.Plugin.registry.keys():
            invocado.plugins.base.Plugin.registry[plugin] = MagicMock()
        self.handler = invocado.Handler()

    def test_loads_plugins(self):
        for p in invocado.plugins.base.Plugin.registry.keys():
            self.assertTrue(hasattr(self.handler, p.lower()))

    def test_state_kwargs(self):
        handler = invocado.Handler(debug=True)
        self.assertTrue(handler.state.debug)

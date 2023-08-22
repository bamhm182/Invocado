"""_handler.py

Defines the Handler class and generally sets up the project.
"""

from ._state import State
from invocado.plugins.base import Plugin


class Handler:
    def __init__(self, state=State(), **kwargs) -> None:
        self.state = state

        for key in kwargs.keys():
            if hasattr(self.state, key):
                setattr(self.state, key, kwargs.get(key))

        for name, subclass in Plugin.registry.items():
            instance = subclass(self.state)
            setattr(self, name.lower(), instance)

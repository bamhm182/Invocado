"""plugins/debug.py

Defines the methods to increase verbosity and aid in debugging
"""

from datetime import datetime

from .base import Plugin


class Debug(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def log(self, title, message):
        if self.state.debug:
            t = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
            print(f'{t} -- {title.upper()}\n\t{message}')

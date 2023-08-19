from .base import Plugin


class Guacamole(Plugin):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for plugin in ['Db']:
            setattr(self,
                    plugin.lower(),
                    self.registry.get(plugin)(self.state))

import alembic.config
import alembic.command
import sqlalchemy as sa
import pathlib

from sqlalchemy.orm import sessionmaker
from invocado.db.models import Config

from .base import Plugin


class Db(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sqlite_db = self.state.config_dir / 'invocado.db'

        self.set_migration()

        engine = sa.create_engine(f'sqlite:///{str(self.sqlite_db)}')
        sa.event.listen(engine, 'connect', self._fk_pragma_on_connect)
        self.Session = sessionmaker(bind=engine)


    @staticmethod
    def _fk_pragma_on_connect(dbapi_con, con_record):
        dbapi_con.execute('pragma foreign_keys=ON')

    def get_config(self, name=None):
        session = self.Session()
        config = session.query(Config).filter_by(id=1).first()
        if not config:
            config = Config()
            session.add(config)
        session.close()
        return getattr(config, name) if name else config

    @property
    def guacamole_host(self) -> str:
        return self.get_config('guacamole_host')

    @guacamole_host.setter
    def guacamole_host(self, value):
        self.set_config('guacamole_host', value)

    @property
    def guacamole_password(self) -> str:
        return self.get_config('guacamole_password')

    @guacamole_password.setter
    def guacamole_password(self, value):
        self.set_config('guacamole_password', value)

    @property
    def guacamole_username(self) -> str:
        return self.get_config('guacamole_username')

    @guacamole_username.setter
    def guacamole_username(self, value):
        self.set_config('guacamole_username', value)

    def set_config(self, name, value):
        session = self.Session()
        config = session.query(Config).filter_by(id=1).first()
        if not config:
            config = Config()
            session.add(config)
        setattr(config, name, value)
        session.commit()
        session.close()

    def set_migration(self):
        db_folder = pathlib.Path(__file__).parent.parent / 'db'

        config = alembic.config.Config()
        config.set_main_option('script_location', str(db_folder / 'alembic'))
        config.set_main_option('version_locations', str(db_folder / 'alembic/versions'))
        config.set_main_option('sqlalchemy.url', f'sqlite:///{str(self.sqlite_db)}')
        alembic.command.upgrade(config, 'head')

    @property
    def terraform_dir(self) -> str:
        return self.get_config('terraform_dir')

    @terraform_dir.setter
    def terraform_dir(self, value):
        self.set_config('terraform_dir', value)

    @property
    def terraform_repo(self) -> str:
        return self.get_config('terraform_repo')

    @terraform_repo.setter
    def terraform_repo(self, value):
        self.set_config('terraform_repo', value)

    @property
    def wol_ip(self) -> str:
        return self.get_config('wol_ip')

    @wol_ip.setter
    def wol_ip(self, value):
        self.set_config('wol_ip', value)

    @property
    def wol_port(self) -> str:
        return self.get_config('wol_port')

    @wol_port.setter
    def wol_port(self, value):
        self.set_config('wol_port', value)

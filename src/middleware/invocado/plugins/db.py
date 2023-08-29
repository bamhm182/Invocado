import alembic.config
import alembic.command
import itertools
import pathlib
import sqlalchemy as sa

from sqlalchemy.orm import sessionmaker
from invocado.db.models import Config
from invocado.db.models import MacMapping
from tabulate import tabulate

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

    def add_mac_mapping(self, mapping) -> None:
        session = self.Session()
        q = session.query(MacMapping)
        for m in mapping:
            db_m = q.filter_by(position=m.get('position'))
            db_m = db_m.filter_by(description=m.get('description')).first()
            if db_m is None:
                db_m = MacMapping()
                session.add(db_m)
                db_m.position = m['position']
                db_m.description = m['description']
                if db_m.value is None:
                    highest = q.filter_by(position=m['position']).order_by(MacMapping.value.desc()).first()
                    if highest.value is None:
                        value = 0
                    else:
                        value = highest.value + 1
                elif type(m['value'] == str):
                    value = int(m['value'], 16)
                else:
                    value = m['value']
                db_m.value = value
        session.commit()
        session.close()

    def get_config(self, name: str = None):
        session = self.Session()
        config = session.query(Config).filter_by(id=1).first()
        if not config:
            config = Config()
            session.add(config)
        session.close()
        return getattr(config, name) if name else config

    def get_mac_mappings(self):
        session = self.Session()
        query = session.query(MacMapping)
        values = list()

        for i in range(6):
            maps = query.filter_by(position=i).all()
            values.append(['FF'] if len(maps) == 0 else [hex(m.value).upper().replace('0X', '000')[-2:] for m in maps])

        session.close()

        return set(':'.join(parts) for parts in itertools.product(*values))

    @property
    def guacamole_authtoken(self) -> str:
        return self.state.guacamole_authtoken

    @guacamole_authtoken.setter
    def guacamole_authtoken(self, value) -> str:
        self.state.guacamole_authtoken = value

    @property
    def guacamole_datasource(self) -> str:
        return self.state.guacamole_datasource

    @guacamole_datasource.setter
    def guacamole_datasource(self, value: str) -> None:
        self.state.guacamole_datasource = value

    @property
    def guacamole_password(self) -> str:
        if self.state.guacamole_password is None:
            return self.get_config('guacamole_password')
        return self.state.guacamole_password

    @guacamole_password.setter
    def guacamole_password(self, value: str) -> None:
        self.state.guacamole_password = value
        self.set_config('guacamole_password', value)

    @property
    def guacamole_url(self) -> str:
        if self.state.guacamole_url is None:
            return self.get_config('guacamole_url')
        return self.state.guacamole_url

    @guacamole_url.setter
    def guacamole_url(self, value: str) -> None:
        self.state.guacamole_url = value
        self.set_config('guacamole_url', value)

    @property
    def guacamole_username(self) -> str:
        if self.state.guacamole_username is None:
            return self.get_config('guacamole_username')
        return self.state.guacamole_username

    @guacamole_username.setter
    def guacamole_username(self, value: str) -> None:
        self.state.guacamole_username = value
        self.set_config('guacamole_username', value)

    def print_mac_mappings(self):
        data = list()
        for mac in self.get_mac_mappings():
            definition = self.decode_mac(mac)
            if definition:
                data.append([
                    definition['mac'],
                    definition['vlan'],
                    definition['folder']
                ])

        data.sort(key=lambda x: x[0])

        print(tabulate(data, headers=['MAC', 'VLAN', 'TF Config']))

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
        if self.state.terraform_dir is None:
            return self.get_config('terraform_dir')
        return self.state.terraform_dir

    @terraform_dir.setter
    def terraform_dir(self, value: str) -> None:
        self.state.terraform_dir = value
        self.set_config('terraform_dir', value)

    @property
    def terraform_repo(self) -> str:
        return self.get_config('terraform_repo')

    @terraform_repo.setter
    def terraform_repo(self, value: str) -> None:
        self.state.terraform_repo = value
        self.set_config('terraform_repo', value)

    @property
    def wol_ip(self) -> str:
        if self.state.wol_ip is None:
            return self.get_config('wol_ip')
        return self.state.wol_ip

    @wol_ip.setter
    def wol_ip(self, value: str) -> None:
        self.state.wol_ip = value
        self.set_config('wol_ip', value)

    @property
    def wol_mac_mapping(self) -> str:
        return self.get_config('wol_mac_mapping')

    @wol_mac_mapping.setter
    def wol_mac_mapping(self, value: str) -> None:
        value = value.upper()
        if len(re.sub(r'[^FVI]', '', value)) != 12:
            return
        used = list()
        previous = None
        for current in value:
            if current in used:
                return
            elif current != previous and previous is not None:
                used.append(previous)
        self.set_config('wol_mac_mapping', value)

    @property
    def wol_port(self) -> int:
        if self.state.wol_port is None:
            return self.get_config('wol_port')
        return self.state.wol_port

    @wol_port.setter
    def wol_port(self, value: str) -> None:
        value = int(value)
        self.state.wol_port = value
        self.set_config('wol_port', value)

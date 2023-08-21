import alembic.config
import alembic.command
import itertools
import pathlib
import re
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

    def decode_mac(self, mac):
        mac = mac.lower()
        if type(mac) == bytes:
            mac = mac.decode()
        MAC_REGEX = re.compile(r'([0-9a-fa-f]{2})')
        positions = MAC_REGEX.findall(mac)

        if len(positions) == 6:
            session = self.Session()
            mappings = session.query(MacMapping)
            config = session.query(Config).filter_by(id=1).first()
            types = {
                0: config.mac_position_type_0,
                1: config.mac_position_type_1,
                2: config.mac_position_type_2,
                3: config.mac_position_type_3,
                4: config.mac_position_type_4,
                5: config.mac_position_type_5
            }
            folder_pos_list = list()
            for key, val in types.items():
                if val == 'instance':
                    instance_pos = key
                elif val == 'vlan':
                    vlan_pos = key
                elif val == 'folder':
                    folder_pos_list.append(key)
            folder_pos_list.sort()

            folder = self.terraform_dir

            for folder_pos in folder_pos_list:
                m = mappings.filter_by(position = folder_pos, value = int(positions[folder_pos], 16)).first()
                if m is not None:
                    folder = folder / m.description

            vlan = mappings.filter_by(position = vlan_pos, value = positions[vlan_pos]).first()
            if vlan is not None:
                vlan = vlan.description

            instance = int(positions[instance_pos], 16)
            vm_name = list()
            vm_name.append(str(folder).replace(str(self.terraform_dir), ''))
            if vlan is not None:
                vm_name.append(f'vlan{vlan}')
            vm_name.append(f'instance{instance}')
            vm_name = '_'.join(vm_name)
            vm_name = vm_name.replace('/', '_').strip('_')

            session.close()

            if folder.exists():
                return {
                    'folder': folder,
                    'instance': instance,
                    'mac': mac.upper(),
                    'vlan': vlan,
                    'vm_name': vm_name
                }

    def get_mac_mappings(self):
        session = self.Session()
        query = session.query(MacMapping)
        values = list()

        for i in range(6):
            maps = query.filter_by(position = i).all()
            values.append([ 'FF' ] if len(maps) == 0 else [hex(m.value).upper().replace('0X', '000')[-2:] for m in maps])

        session.close()

        return set(':'.join(parts) for parts in itertools.product(*values))

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

    def get_config(self, name:str=None):
        session = self.Session()
        config = session.query(Config).filter_by(id=1).first()
        if not config:
            config = Config()
            session.add(config)
        session.close()
        return getattr(config, name) if name else config

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
    def guacamole_url(self) -> str:
        if self.state.guacamole_url is None:
            return self.get_config('guacamole_url')
        return self.state.guacamole_url

    @guacamole_url.setter
    def guacamole_url(self, value: str) -> None:
        self.state.guacamole_url = value
        self.set_config('guacamole_url', value)

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
    def guacamole_username(self) -> str:
        if self.state.guacamole_username is None:
            return self.get_config('guacamole_username')
        return self.state.guacamole_username

    @guacamole_username.setter
    def guacamole_username(self, value: str) -> None:
        self.state.guacamole_username = value
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
    def wol_port(self) -> int:
        if self.state.wol_port is None:
            return self.get_config('wol_port')
        return self.state.wol_port

    @wol_port.setter
    def wol_port(self, value: str) -> None:
        value = int(value)
        self.state.wol_port = value
        self.set_config('wol_port', value)

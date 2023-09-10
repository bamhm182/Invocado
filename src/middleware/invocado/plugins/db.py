import alembic.config
import alembic.command
import itertools
import pathlib
import re
import sqlalchemy

from sqlalchemy.orm import sessionmaker
from invocado.db.models import Config, TerraformFolder, TerraformVLAN
from tabulate import tabulate

from .base import Plugin


class Db(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for plugin in ['Utils']:
            setattr(self,
                    plugin.lower(),
                    self.registry.get(plugin)(self.state))

        self.session_maker = kwargs.get('establish_db', self.establish_db)()

    @staticmethod
    def _fk_pragma_on_connect(dbapi_con, con_record):
        dbapi_con.execute('pragma foreign_keys=ON')

    def add_tf_folders(self, folders: list) -> None:
        folders = self.strip_existing_tf_folders(folders)

        session = self.session_maker()
        for folder in folders:
            db_folder = TerraformFolder(path=folder)
            session.add(db_folder)
        session.commit()
        session.close()

    def establish_db(self):
        db_folder = pathlib.Path(__file__).parent.parent / 'db'
        sqlite_db = self.state.config_dir / 'invocado.db'

        config = alembic.config.Config()
        config.set_main_option('script_location', str(db_folder / 'alembic'))
        config.set_main_option('version_locations', str(db_folder / 'alembic/versions'))
        config.set_main_option('sqlalchemy.url', f'sqlite:///{str(sqlite_db)}')
        alembic.command.upgrade(config, 'head')

        engine = sqlalchemy.create_engine(f'sqlite:///{str(sqlite_db)}')
        sqlalchemy.event.listen(engine, 'connect', self._fk_pragma_on_connect)
        return sessionmaker(bind=engine)

    def get_config(self, name: str = None):
        session = self.session_maker()
        config = session.query(Config).filter_by(id=1).first()
        if not config:
            config = Config()
            session.add(config)
        session.close()
        return getattr(config, name) if name else config

    def get_mac_mappings(self):
        """Returns a set of MAC Addresses which can be used with Invocado
        """
        session = self.session_maker()
        if 'F' in self.wol_mac_mapping:
            folders = session.query(TerraformFolder).all()
        if 'V' in self.wol_mac_mapping:
            vlans = session.query(TerraformVLAN).all()

        session.close()

        macs = list()

        folders_length = self.wol_mac_mapping.count('F')
        vlans_length = self.wol_mac_mapping.count('V')
        instances_length = self.wol_mac_mapping.count('I')

        if len(vlans) == 0:
            vlans = [TerraformVLAN(id=int('F'*vlans_length, 16), name='Default')]

        squashed_mapping = ''.join(c for c, _ in itertools.groupby(self.wol_mac_mapping))
        squashed_mapping = squashed_mapping.replace('F', '__FOLDER__')
        squashed_mapping = squashed_mapping.replace('V', '__VLAN__')
        squashed_mapping = squashed_mapping.replace('I', '__INSTANCE__')

        for folder in folders:
            for vlan in vlans:
                folder_hex = f'000000000000{hex(folder.id).upper().strip("0X")}'[-folders_length:]
                vlan_hex = f'000000000000{hex(vlan.id).upper().strip("0X")}'[-vlans_length:]
                instance_hex = 'FFFFFFFFFFFF'[-instances_length:]
                current_mac = squashed_mapping.replace('__FOLDER__', folder_hex)
                current_mac = current_mac.replace('__VLAN__', vlan_hex)
                current_mac = current_mac.replace('__INSTANCE__', instance_hex)
                macs.append(current_mac)

        returns = {
            'macs': set(),
            'folders': dict(),
            'vlans': dict(),
        }

        for mac in macs:
            returns['macs'].add(':'.join([mac[i:i+2] for i in range(0, len(mac), 2)]))

        for folder in folders:
            returns['folders'][folder.id] = folder.path

        for vlan in vlans:
            returns['vlans'][vlan.id] = vlan.name

        return returns

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
        wol_mac_mapping = self.wol_mac_mapping
        mappings = self.get_mac_mappings()
        for mac in mappings.get('macs'):
            definition = self.utils.decode_mac(mac, wol_mac_mapping)
            if definition:
                data.append([
                    definition['mac'],
                    f'{mappings.get("vlans", dict()).get(definition["vlan"])} ({definition["vlan"]})',
                    f'{mappings.get("folders", dict()).get(definition["folder"])} ({definition["folder"]})',
                ])

        data.sort(key=lambda x: x[0])

        wol_mac_mapping = self.wol_mac_mapping

        print('Your WoL MAC Mapping is ' +
              ':'.join([wol_mac_mapping[i:i+2] for i in range(0, len(wol_mac_mapping), 2)]))
        print('  F: Folder\n  V: VLAN\n  I: Instance\n')
        print(tabulate(data, headers=['MAC', 'VLAN', 'Terraform Folder']))

    def prune_terraform_folders(self):
        session = self.session_maker()
        folders = session.query(TerraformFolder).all()
        tf_dir = pathlib.Path(self.terraform_dir)
        for folder in folders:
            if not (tf_dir / folder.path / 'main.tf').exists():
                session.delete(folder)
        session.commit()
        session.close()

    def set_config(self, name, value):
        session = self.session_maker()
        config = session.query(Config).filter_by(id=1).first()
        if not config:
            config = Config()
            session.add(config)
        setattr(config, name, value)
        session.commit()
        session.close()

    def strip_existing_tf_folders(self, folders) -> list:
        session = self.session_maker()
        query = session.query(TerraformFolder)
        ret = list()
        for folder in folders:
            db_folder = query.filter_by(path=folder).first()
            if not db_folder:
                ret.append(folder)
        session.close()
        return ret

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
            previous = current
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

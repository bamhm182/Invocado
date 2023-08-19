import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Config(Base):
    __tablename__ = 'config'
    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    guacamole_host = sa.Column(sa.VARCHAR(200), default='')
    guacamole_password = sa.Column(sa.VARCHAR(200), default='')
    guacamole_username = sa.Column(sa.VARCHAR(200), default='')
    mac_position_type_0 = sa.Column(sa.VARCHAR(100), default='folder')
    mac_position_type_1 = sa.Column(sa.VARCHAR(100), default='folder')
    mac_position_type_2 = sa.Column(sa.VARCHAR(100), default='folder')
    mac_position_type_3 = sa.Column(sa.VARCHAR(100), default='folder')
    mac_position_type_4 = sa.Column(sa.VARCHAR(100), default='vlan')
    mac_position_type_5 = sa.Column(sa.VARCHAR(100), default='instance')
    terraform_dir = sa.Column(sa.VARCHAR(300), default='~/.config/invocado/terraform')
    terraform_repo = sa.Column(sa.VARCHAR(300), default='')
    wol_ip = sa.Column(sa.VARCHAR(100), default='127.0.0.1')
    wol_port = sa.Column(sa.INTEGER, default=9)

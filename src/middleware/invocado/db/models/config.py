import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Config(Base):
    __tablename__ = 'config'
    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    guacamole_host = sa.Column(sa.VARCHAR(200), default='')
    guacamole_password = sa.Column(sa.VARCHAR(200), default='')
    guacamole_username = sa.Column(sa.VARCHAR(200), default='')
    terraform_dir = sa.Column(sa.VARCHAR(300), default='~/.config/invocado/terraform')
    terraform_repo = sa.Column(sa.VARCHAR(300), default='')
    wol_ip = sa.Column(sa.VARCHAR(100), default='127.0.0.1')
    wol_port = sa.Column(sa.INTEGER, default=9)

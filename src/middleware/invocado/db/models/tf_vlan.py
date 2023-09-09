"""db/models/tf_vlan.py

"""

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class TerraformVLAN(Base):
    __tablename__ = 'tf_vlan'
    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    name = sa.Column(sa.VARCHAR(128))

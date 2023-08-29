"""
db/models/mac_mapping.py

"""

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class MacMapping(Base):
    __tablename__ = 'mac_mapping'
    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    kind = sa.Column(sa.CHAR(1))
    value = sa.Column(sa.INTEGER)
    description = sa.Column(sa.VARCHAR(100), default='')

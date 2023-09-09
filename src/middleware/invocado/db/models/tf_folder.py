"""
db/models/tf_folder.py

"""

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class TerraformFolder(Base):
    __tablename__ = 'tf_folder'
    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    path = sa.Column(sa.VARCHAR(256), default='')

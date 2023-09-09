"""db/models/tf_instance.py

"""

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

from .tf_folder import TerraformFolder

Base = declarative_base()


class TerraformInstance(Base):
    __tablename__ = 'tf_instance'
    id = sa.Column(sa.INTEGER, autoincrement=True, primary_key=True)
    number = sa.Column(sa.INTEGER)
    folder = sa.Column(sa.ForeignKey(TerraformFolder.id))

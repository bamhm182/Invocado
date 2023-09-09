"""initial revision

Revision ID: f46f81da4b7a
Revises:
Create Date: 2023-08-19 01:07:18.137609

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f46f81da4b7a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('config',
                    sa.Column('id', sa.INTEGER, primary_key=True),
                    sa.Column('guacamole_datasource', sa.VARCHAR(50), server_default=''),
                    sa.Column('guacamole_url', sa.VARCHAR(200), server_default='http://127.0.0.1:8080/guacamole/'),
                    sa.Column('guacamole_password', sa.VARCHAR(200), server_default='guacadmin'),
                    sa.Column('guacamole_username', sa.VARCHAR(200), server_default='guacadmin'),
                    sa.Column('wol_mac_mapping', sa.CHAR(12), server_default='FFFFFFVVIIII'),
                    sa.Column('terraform_dir', sa.VARCHAR(300), server_default='~/.config/invocado/terraform'),
                    sa.Column('terraform_repo', sa.VARCHAR(300), server_default=''),
                    sa.Column('wol_ip', sa.VARCHAR(100), server_default='127.0.0.1'),
                    sa.Column('wol_port', sa.INTEGER, default=9))
    op.create_table('tf_folder',
                    sa.Column('id', sa.INTEGER, primary_key=True),
                    sa.Column('path', sa.VARCHAR(256)))
    op.create_table('tf_instance',
                    sa.Column('id', sa.INTEGER, primary_key=True),
                    sa.Column('number', sa.INTEGER),
                    sa.Column('folder', sa.INTEGER, sa.ForeignKey('tf_folder.id')))
    op.create_table('tf_vlan',
                    sa.Column('id', sa.INTEGER, primary_key=True),
                    sa.Column('name', sa.VARCHAR(128)))


def downgrade() -> None:
    op.drop_table('config')
    op.drop_table('tf_folder')
    op.drop_table('tf_instance')
    op.drop_table('tf_vlan')

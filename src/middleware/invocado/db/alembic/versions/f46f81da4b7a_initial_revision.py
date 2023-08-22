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
                    sa.Column('guacamole_url', sa.VARCHAR(200), server_default='http://127.0.0.1:8080/guacamole/'),
                    sa.Column('guacamole_password', sa.VARCHAR(200), server_default='guacadmin'),
                    sa.Column('guacamole_username', sa.VARCHAR(200), server_default='guacadmin'),
                    sa.Column('mac_position_type_0', sa.VARCHAR(100), server_default='folder'),
                    sa.Column('mac_position_type_1', sa.VARCHAR(100), server_default='folder'),
                    sa.Column('mac_position_type_2', sa.VARCHAR(100), server_default='folder'),
                    sa.Column('mac_position_type_3', sa.VARCHAR(100), server_default='folder'),
                    sa.Column('mac_position_type_4', sa.VARCHAR(100), server_default='vlan'),
                    sa.Column('mac_position_type_5', sa.VARCHAR(100), server_default='instance'),
                    sa.Column('terraform_dir', sa.VARCHAR(300), server_default='~/.config/invocado/terraform'),
                    sa.Column('terraform_repo', sa.VARCHAR(300), server_default=''),
                    sa.Column('wol_ip', sa.VARCHAR(100), server_default='127.0.0.1'),
                    sa.Column('wol_port', sa.INTEGER, default=9))
    op.create_table('mac_mapping',
                    sa.Column('id', sa.INTEGER, primary_key=True),
                    sa.Column('position', sa.INTEGER, server_default=None),
                    sa.Column('value', sa.INTEGER, server_default=None),
                    sa.Column('description', sa.VARCHAR(100), server_default=''))


def downgrade() -> None:
    op.drop_table('config')
    op.drop_table('mac_mapping')

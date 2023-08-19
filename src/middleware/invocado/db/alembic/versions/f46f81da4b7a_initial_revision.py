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
                    sa.Column('guacamole_host', sa.VARCHAR(200), server_default=''),
                    sa.Column('guacamole_password', sa.VARCHAR(200), server_default=''),
                    sa.Column('guacamole_username', sa.VARCHAR(200), server_default=''),
                    sa.Column('terraform_dir', sa.VARCHAR(300), server_default='~/.config/invocado/terraform'),
                    sa.Column('terraform_repo', sa.VARCHAR(300), server_default=''),
                    sa.Column('wol_ip', sa.VARCHAR(100), server_default='127.0.0.1'),
                    sa.Column('wol_port', sa.INTEGER, default=9))


def downgrade() -> None:
    op.drop_table('config')

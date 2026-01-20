""""add_missing_user_fields"

Revision ID: 7e76f7f3876d
Revises: 
Create Date: 2026-01-20 16:05:10.168701
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7e76f7f3876d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Add organization_id if it doesn't exist
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [c['name'] for c in inspector.get_columns('users')]

    if 'organization_id' not in columns:
        op.add_column('users', sa.Column('organization_id', sa.UUID(), nullable=True))
        op.create_foreign_key('fk_users_organization', 'users', 'organizations', ['organization_id'], ['id'], ondelete='CASCADE')
        op.create_index(op.f('ix_users_organization_id'), 'users', ['organization_id'], unique=False)
    
    if 'phone' not in columns:
        op.add_column('users', sa.Column('phone', sa.String(length=50), nullable=True))
    
    if 'timezone' not in columns:
        op.add_column('users', sa.Column('timezone', sa.String(length=50), server_default='UTC', nullable=True))
    
    if 'language' not in columns:
        op.add_column('users', sa.Column('language', sa.String(length=10), server_default='en', nullable=True))
    
    if 'preferences' not in columns:
        op.add_column('users', sa.Column('preferences', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=True))

def downgrade() -> None:
    op.drop_index(op.f('ix_users_organization_id'), table_name='users')
    op.drop_constraint('fk_users_organization', 'users', type_='foreignkey')
    op.drop_column('users', 'preferences')
    op.drop_column('users', 'language')
    op.drop_column('users', 'timezone')
    op.drop_column('users', 'phone')
    op.drop_column('users', 'organization_id')

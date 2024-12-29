"""drop existing enums

Revision ID: drop_enums_001
Revises: 
Create Date: 2024-03-21
"""
from alembic import op

# revision identifiers
revision = 'drop_enums_001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Drop the tables that use these enums first
    op.execute('DROP TABLE IF EXISTS tasks CASCADE;')
    
    # Drop the enum types
    op.execute('DROP TYPE IF EXISTS taskstatus CASCADE;')
    op.execute('DROP TYPE IF EXISTS taskpriority CASCADE;')

def downgrade():
    # Create the enum types
    op.execute("CREATE TYPE taskstatus AS ENUM ('TODO', 'IN_PROGRESS', 'DONE', 'BLOCKED', 'REOPENED');")
    op.execute("CREATE TYPE taskpriority AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'URGENT');") 
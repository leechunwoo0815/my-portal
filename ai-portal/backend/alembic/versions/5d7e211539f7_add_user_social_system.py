"""add_user_social_system

Revision ID: 5d7e211539f7
Revises: 563847e73f35
Create Date: 2026-05-09 14:32:14.444016

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5d7e211539f7'
down_revision = '563847e73f35'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add columns directly
    op.add_column('blogs', sa.Column('author_id', sa.Integer(), nullable=True))
    op.add_column('blogs', sa.Column('likes_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('blogs', sa.Column('favorites_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('blogs', sa.Column('shares_count', sa.Integer(), nullable=False, server_default='0'))

    op.add_column('projects', sa.Column('author_id', sa.Integer(), nullable=True))
    op.add_column('projects', sa.Column('likes_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('projects', sa.Column('favorites_count', sa.Integer(), nullable=False, server_default='0'))

    op.add_column('comments', sa.Column('user_id', sa.Integer(), nullable=True))

    op.add_column('users', sa.Column('nickname', sa.String(length=50), nullable=True))
    op.add_column('users', sa.Column('bio', sa.String(length=500), nullable=True))
    op.add_column('users', sa.Column('level', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('users', sa.Column('points', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('total_points', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('followers_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('following_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('gender', sa.String(length=10), nullable=True))
    op.add_column('users', sa.Column('location', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('website', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('github', sa.String(length=255), nullable=True))

    # Create new tables
    op.create_table('moments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('images', sa.JSON(), nullable=True),
        sa.Column('moment_type', sa.String(length=20), nullable=False),
        sa.Column('original_id', sa.Integer(), nullable=True),
        sa.Column('likes_count', sa.Integer(), nullable=False),
        sa.Column('comments_count', sa.Integer(), nullable=False),
        sa.Column('is_public', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['original_id'], ['moments.id'], name='fk_moments_original_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_moments_user_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_moments_id'), 'moments', ['id'], unique=False)

    op.create_table('user_follows',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('follower_id', sa.Integer(), nullable=False),
        sa.Column('following_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['follower_id'], ['users.id'], name='fk_user_follows_follower_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['following_id'], ['users.id'], name='fk_user_follows_following_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('follower_id', 'following_id', name='uq_user_follow_pair')
    )
    op.create_index(op.f('ix_user_follows_id'), 'user_follows', ['id'], unique=False)

    op.create_table('direct_messages',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('receiver_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['receiver_id'], ['users.id'], name='fk_direct_messages_receiver_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], name='fk_direct_messages_sender_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_direct_messages_id'), 'direct_messages', ['id'], unique=False)

    op.create_table('notifications',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('from_user_id', sa.Integer(), nullable=True),
        sa.Column('target_type', sa.String(length=20), nullable=True),
        sa.Column('target_id', sa.Integer(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['from_user_id'], ['users.id'], name='fk_notifications_from_user_id', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_notifications_user_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)

    op.create_table('user_likes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('target_type', sa.String(length=20), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_user_likes_user_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'target_type', 'target_id', name='uq_user_like')
    )
    op.create_index(op.f('ix_user_likes_id'), 'user_likes', ['id'], unique=False)

    op.create_table('user_favorites',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('target_type', sa.String(length=20), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_user_favorites_user_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'target_type', 'target_id', name='uq_user_favorite')
    )
    op.create_index(op.f('ix_user_favorites_id'), 'user_favorites', ['id'], unique=False)

    op.create_table('point_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=30), nullable=False),
        sa.Column('points', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_point_logs_user_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_point_logs_id'), 'point_logs', ['id'], unique=False)


def downgrade() -> None:
    op.drop_table('point_logs')
    op.drop_table('user_favorites')
    op.drop_table('user_likes')
    op.drop_table('notifications')
    op.drop_table('direct_messages')
    op.drop_table('user_follows')
    op.drop_table('moments')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('github')
        batch_op.drop_column('website')
        batch_op.drop_column('location')
        batch_op.drop_column('gender')
        batch_op.drop_column('following_count')
        batch_op.drop_column('followers_count')
        batch_op.drop_column('total_points')
        batch_op.drop_column('points')
        batch_op.drop_column('level')
        batch_op.drop_column('bio')
        batch_op.drop_column('nickname')

    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.drop_column('favorites_count')
        batch_op.drop_column('likes_count')
        batch_op.drop_column('author_id')

    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.drop_column('user_id')

    with op.batch_alter_table('blogs', schema=None) as batch_op:
        batch_op.drop_column('shares_count')
        batch_op.drop_column('favorites_count')
        batch_op.drop_column('likes_count')
        batch_op.drop_column('author_id')

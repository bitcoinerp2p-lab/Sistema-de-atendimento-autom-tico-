"""initial schema — leads, events, agent_reputation, pending_funnel_updates

Revision ID: 0001
Revises:
Create Date: 2026-07-07

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "leads",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("phone", sa.String(), nullable=False, unique=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("current_stage", sa.String(), nullable=False, server_default="funnel_1_captacao"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_leads_phone", "leads", ["phone"])

    op.create_table(
        "events",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("actor_source", sa.String(), nullable=False),
        sa.Column("lead_id", sa.String(), sa.ForeignKey("leads.id"), nullable=True),
        sa.Column("payload_data", sa.JSON(), nullable=False),
        sa.Column("auth_signature", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_events_event_type", "events", ["event_type"])
    op.create_index("ix_events_actor_source", "events", ["actor_source"])
    op.create_index("ix_events_lead_id", "events", ["lead_id"])
    op.create_index("ix_events_created_at", "events", ["created_at"])

    op.create_table(
        "agent_reputation",
        sa.Column("agent_identifier", sa.String(), primary_key=True),
        sa.Column("score", sa.Float(), nullable=False, server_default="10.0"),
        sa.Column("successful_interactions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "pending_funnel_updates",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("source_agent", sa.String(), nullable=False),
        sa.Column("proposed_text", sa.Text(), nullable=False),
        sa.Column("context_objection", sa.Text(), nullable=True),
        sa.Column("is_approved", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_by", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("pending_funnel_updates")
    op.drop_table("agent_reputation")
    op.drop_index("ix_events_created_at", table_name="events")
    op.drop_index("ix_events_lead_id", table_name="events")
    op.drop_index("ix_events_actor_source", table_name="events")
    op.drop_index("ix_events_event_type", table_name="events")
    op.drop_table("events")
    op.drop_index("ix_leads_phone", table_name="leads")
    op.drop_table("leads")

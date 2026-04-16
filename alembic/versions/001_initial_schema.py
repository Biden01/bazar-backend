"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-28
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("phone", sa.String(20), unique=True, index=True, nullable=False),
        sa.Column("name", sa.String(100)),
        sa.Column("role", sa.String(10), server_default="buyer"),
        sa.Column("avatar_url", sa.String(500)),
        sa.Column("location", sa.String(200)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("seller_id", sa.Integer(), sa.ForeignKey("users.id"), index=True, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("category", sa.String(50), index=True, nullable=False),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("wholesale_price", sa.Integer()),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("stock", sa.Integer(), server_default="0"),
        sa.Column("min_order", sa.Integer(), server_default="1"),
        sa.Column("description", sa.Text()),
        sa.Column("rating", sa.Float(), server_default="0"),
        sa.Column("review_count", sa.Integer(), server_default="0"),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "product_images",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), index=True),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0"),
    )

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("buyer_id", sa.Integer(), sa.ForeignKey("users.id"), index=True, nullable=False),
        sa.Column("seller_id", sa.Integer(), sa.ForeignKey("users.id"), index=True, nullable=False),
        sa.Column("status", sa.String(20), server_default="new"),
        sa.Column("delivery_type", sa.String(20), nullable=False),
        sa.Column("payment_method", sa.String(20), nullable=False),
        sa.Column("address", sa.String(300)),
        sa.Column("total", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id", ondelete="CASCADE"), index=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id")),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("price", sa.Integer(), nullable=False),
    )

    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id"), index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), index=True),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "inventory",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("seller_id", sa.Integer(), sa.ForeignKey("users.id"), index=True, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("stock", sa.Integer(), server_default="0"),
        sa.Column("min_stock", sa.Integer(), server_default="0"),
        sa.Column("is_public", sa.Boolean(), server_default="true"),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("image_url", sa.String(500)),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "debts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("seller_id", sa.Integer(), sa.ForeignKey("users.id"), index=True, nullable=False),
        sa.Column("buyer_name", sa.String(200), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("paid_amount", sa.Integer(), server_default="0"),
        sa.Column("status", sa.String(20), server_default="pending"),
        sa.Column("description", sa.Text()),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "debt_payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("debt_id", sa.Integer(), sa.ForeignKey("debts.id", ondelete="CASCADE"), index=True),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), server_default=sa.func.current_date()),
    )

    op.create_table(
        "chats",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("buyer_id", sa.Integer(), sa.ForeignKey("users.id"), index=True, nullable=False),
        sa.Column("seller_id", sa.Integer(), sa.ForeignKey("users.id"), index=True, nullable=False),
        sa.Column("last_message_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("chat_id", sa.Integer(), sa.ForeignKey("chats.id", ondelete="CASCADE"), index=True),
        sa.Column("sender_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), index=True, nullable=False),
        sa.Column("type", sa.String(30), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "b2b_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), unique=True, index=True),
        sa.Column("business_name", sa.String(200), nullable=False),
        sa.Column("business_type", sa.String(50), nullable=False),
        sa.Column("ip_number", sa.String(50), nullable=False),
        sa.Column("verification_status", sa.String(20), server_default="pending"),
        sa.Column("document_url", sa.String(500)),
        sa.Column("shop_photo_url", sa.String(500)),
        sa.Column("lat", sa.Float()),
        sa.Column("lon", sa.Float()),
    )

    op.create_table(
        "price_groups",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("discount_percent", sa.Integer(), server_default="0"),
        sa.Column("description", sa.Text()),
    )

    op.create_table(
        "price_group_members",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("price_group_id", sa.Integer(), sa.ForeignKey("price_groups.id"), index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), index=True),
    )

    op.create_table(
        "price_group_products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("price_group_id", sa.Integer(), sa.ForeignKey("price_groups.id"), index=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), index=True),
        sa.Column("special_price", sa.Integer(), nullable=False),
    )

    op.create_table(
        "vet_certs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("seller_id", sa.Integer(), sa.ForeignKey("users.id"), index=True),
        sa.Column("number", sa.String(50), nullable=False),
        sa.Column("product", sa.String(200), nullable=False),
        sa.Column("issue_date", sa.Date(), nullable=False),
        sa.Column("expiry_date", sa.Date(), nullable=False),
        sa.Column("issuer", sa.String(200), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("document_url", sa.String(500)),
    )

    op.create_table(
        "invoices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("seller_id", sa.Integer(), sa.ForeignKey("users.id"), index=True),
        sa.Column("buyer_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("number", sa.String(50), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("item_count", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), server_default="pending"),
    )


def downgrade() -> None:
    op.drop_table("invoices")
    op.drop_table("vet_certs")
    op.drop_table("price_group_products")
    op.drop_table("price_group_members")
    op.drop_table("price_groups")
    op.drop_table("b2b_profiles")
    op.drop_table("notifications")
    op.drop_table("messages")
    op.drop_table("chats")
    op.drop_table("debt_payments")
    op.drop_table("debts")
    op.drop_table("inventory")
    op.drop_table("reviews")
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("product_images")
    op.drop_table("products")
    op.drop_table("users")

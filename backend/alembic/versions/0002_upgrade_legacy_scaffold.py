"""Upgrade databases created from the original scaffold's 0001 schema.

This is intentionally conditional: fresh installs already receive the current
domain tables from 0001, while early demo databases may have recorded the same
revision ID with the former risk_zones/shelters layout.
"""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

revision = "0002_upgrade_legacy_scaffold"
down_revision = "0001_initial_postgis"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table("areas"):
        return

    op.create_table(
        "areas",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("geometry", Geometry("POLYGON", srid=4326), nullable=False),
        sa.Column("population", sa.Integer(), nullable=False),
        sa.Column("elderly_pct", sa.Float(), nullable=False, server_default="0"),
        sa.Column("children_pct", sa.Float(), nullable=False, server_default="0"),
        sa.Column("historical_disaster_count", sa.Integer(), nullable=False, server_default="0"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_areas_name", "areas", ["name"])
    op.create_table(
        "hazard_layers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("area_id", sa.Integer(), sa.ForeignKey("areas.id", ondelete="SET NULL")),
        sa.Column("hazard_type", sa.String(30), nullable=False),
        sa.Column("intensity", sa.Float(), nullable=False),
        sa.Column("geometry", Geometry("POLYGON", srid=4326), nullable=False),
        sa.CheckConstraint("hazard_type IN ('flood', 'landslide', 'rainfall')", name="ck_hazard_type"),
        sa.CheckConstraint("intensity >= 0 AND intensity <= 1", name="ck_hazard_intensity"),
    )
    op.create_index("ix_hazard_layers_area_id", "hazard_layers", ["area_id"])
    op.create_table("road_segments", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("geometry", Geometry("LINESTRING", srid=4326), nullable=False), sa.Column("passes_hazard_zone", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("length_km", sa.Float(), nullable=False))

    # Legacy shelters used `location`; preserve all existing rows while making
    # the column name match the current ORM and assuming road access until GIS
    # data supplies a more precise value.
    shelter_columns = {column["name"] for column in inspector.get_columns("shelters")}
    if "location" in shelter_columns and "geometry" not in shelter_columns:
        op.alter_column("shelters", "location", new_column_name="geometry", existing_type=Geometry("POINT", srid=4326))
    if "road_accessible" not in shelter_columns:
        op.add_column("shelters", sa.Column("road_accessible", sa.Boolean(), nullable=False, server_default=sa.true()))

    if inspector.has_table("risk_zones"):
        op.execute("INSERT INTO areas (name, geometry, population, elderly_pct, children_pct, historical_disaster_count) SELECT area_id, geometry, population, 0, 0, 0 FROM risk_zones")


def downgrade() -> None:
    # This conditional compatibility migration cannot safely distinguish a
    # fresh 0001 database from a legacy one during downgrade.
    pass

"""Create the initial PostGIS schema for district datasets."""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

revision = "0001_initial_postgis"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.create_table("areas", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(150), nullable=False), sa.Column("geometry", Geometry("POLYGON", srid=4326), nullable=False), sa.Column("population", sa.Integer(), nullable=False), sa.Column("elderly_pct", sa.Float(), nullable=False), sa.Column("children_pct", sa.Float(), nullable=False), sa.Column("historical_disaster_count", sa.Integer(), nullable=False), sa.UniqueConstraint("name"))
    op.create_index("ix_areas_name", "areas", ["name"])
    op.create_table("hazard_layers", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("area_id", sa.Integer(), sa.ForeignKey("areas.id", ondelete="SET NULL"), nullable=True), sa.Column("hazard_type", sa.String(30), nullable=False), sa.Column("intensity", sa.Float(), nullable=False), sa.Column("geometry", Geometry("POLYGON", srid=4326), nullable=False), sa.CheckConstraint("hazard_type IN ('flood', 'landslide', 'rainfall')", name="ck_hazard_type"), sa.CheckConstraint("intensity >= 0 AND intensity <= 1", name="ck_hazard_intensity"))
    op.create_index("ix_hazard_layers_area_id", "hazard_layers", ["area_id"])
    op.create_table("shelters", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(255), nullable=False), sa.Column("geometry", Geometry("POINT", srid=4326), nullable=False), sa.Column("capacity", sa.Integer(), nullable=False), sa.Column("medical_facility", sa.Boolean(), nullable=False), sa.Column("water_available", sa.Boolean(), nullable=False), sa.Column("road_accessible", sa.Boolean(), nullable=False), sa.UniqueConstraint("name"))
    op.create_index("ix_shelters_name", "shelters", ["name"])
    op.create_table("road_segments", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("geometry", Geometry("LINESTRING", srid=4326), nullable=False), sa.Column("passes_hazard_zone", sa.Boolean(), nullable=False), sa.Column("length_km", sa.Float(), nullable=False))

def downgrade() -> None:
    op.drop_table("road_segments")
    op.drop_table("shelters")
    op.drop_table("hazard_layers")
    op.drop_table("areas")

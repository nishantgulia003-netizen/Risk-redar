"""Load a small, entirely synthetic district dataset into PostGIS.

This is placeholder data, not a representation of a real place. The Data/GIS
teammate can export GeoJSON FeatureCollections and call load_district_geojson
with the same four arguments to replace it without changing the application.
"""
from pathlib import Path
import sys

from geoalchemy2.shape import from_shape
from shapely.geometry import LineString, Point, Polygon, shape
from sqlalchemy import delete

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.db.session import SessionLocal
from app.models import Area, HazardLayer, RoadSegment, Shelter


def feature(geometry, **properties):
    return {"type": "Feature", "geometry": geometry.__geo_interface__, "properties": properties}


def load_district_geojson(session, areas_geojson, hazards_geojson, shelters_geojson, roads_geojson) -> None:
    """Load four GeoJSON FeatureCollections supplied by synthetic or GIS exports."""
    area_by_source_id: dict[str, Area] = {}
    for item in areas_geojson["features"]:
        p = item["properties"]
        area = Area(name=p["name"], geometry=from_shape(shape(item["geometry"]), srid=4326), population=p["population"], elderly_pct=p["elderly_pct"], children_pct=p["children_pct"], historical_disaster_count=p["historical_disaster_count"])
        session.add(area)
        session.flush()
        area_by_source_id[str(p["source_id"])] = area
    for item in hazards_geojson["features"]:
        p = item["properties"]
        session.add(HazardLayer(area_id=area_by_source_id.get(str(p.get("area_source_id"))).id if p.get("area_source_id") is not None else None, hazard_type=p["hazard_type"], intensity=p["intensity"], geometry=from_shape(shape(item["geometry"]), srid=4326)))
    for item in shelters_geojson["features"]:
        p = item["properties"]
        session.add(Shelter(name=p["name"], geometry=from_shape(shape(item["geometry"]), srid=4326), capacity=p["capacity"], medical_facility=p["medical_facility"], water_available=p["water_available"], road_accessible=p["road_accessible"]))
    for item in roads_geojson["features"]:
        p = item["properties"]
        session.add(RoadSegment(geometry=from_shape(shape(item["geometry"]), srid=4326), passes_hazard_zone=p["passes_hazard_zone"], length_km=p["length_km"]))


def synthetic_geojson():
    """Create 12 areas, three hazard layers, seven shelters, and 23 road segments."""
    lon, lat, step = 77.50, 12.90, 0.012
    areas = []
    for row in range(3):
        for col in range(4):
            index = row * 4 + col + 1
            polygon = Polygon([(lon + col * step, lat + row * step), (lon + (col + 1) * step, lat + row * step), (lon + (col + 1) * step, lat + (row + 1) * step), (lon + col * step, lat + (row + 1) * step)])
            areas.append(feature(polygon, source_id=index, name=f"Sample District Zone {index:02d}", population=2800 + index * 390, elderly_pct=7.5 + (index % 5) * 1.8, children_pct=18.0 + (index % 4) * 2.7, historical_disaster_count=index % 5))
    hazards = [feature(Polygon([(lon, lat), (lon + 2*step, lat), (lon + 2*step, lat + 3*step), (lon, lat + 3*step)]), area_source_id=1, hazard_type="flood", intensity=0.82), feature(Polygon([(lon + 2*step, lat + step), (lon + 4*step, lat + step), (lon + 4*step, lat + 3*step), (lon + 2*step, lat + 3*step)]), area_source_id=7, hazard_type="landslide", intensity=0.63), feature(Polygon([(lon + step, lat), (lon + 4*step, lat), (lon + 4*step, lat + step), (lon + step, lat + step)]), area_source_id=2, hazard_type="rainfall", intensity=0.46)]
    shelters = [feature(Point(lon + (i % 4 + .5) * step, lat + (i // 4 + .5) * step), name=f"Community Shelter {i + 1}", capacity=3500 + i * 750, medical_facility=i in (0, 3), water_available=i != 5, road_accessible=True) for i in range(7)]
    # A connected centre-to-centre grid: 9 horizontal + 8 vertical + 6 diagonal links.
    nodes = {(r, c): (lon + (c + .5) * step, lat + (r + .5) * step) for r in range(3) for c in range(4)}
    lines = []
    for r in range(3):
        for c in range(3): lines.append(LineString([nodes[r, c], nodes[r, c + 1]]))
    for r in range(2):
        for c in range(4): lines.append(LineString([nodes[r, c], nodes[r + 1, c]]))
    for r in range(2):
        for c in range(3): lines.append(LineString([nodes[r, c], nodes[r + 1, c + 1]]))
    roads = [feature(line, passes_hazard_zone=(i % 6 == 0), length_km=round(1.25 + (i % 4) * .12, 2)) for i, line in enumerate(lines)]
    return {"type": "FeatureCollection", "features": areas}, {"type": "FeatureCollection", "features": hazards}, {"type": "FeatureCollection", "features": shelters}, {"type": "FeatureCollection", "features": roads}


def main() -> None:
    areas, hazards, shelters, roads = synthetic_geojson()
    with SessionLocal.begin() as session:
        # Seeder reset is intentional and scoped only to the four synthetic tables.
        session.execute(delete(RoadSegment)); session.execute(delete(Shelter)); session.execute(delete(HazardLayer)); session.execute(delete(Area))
        load_district_geojson(session, areas, hazards, shelters, roads)
    print("Loaded synthetic RiskRadar district dataset.")


if __name__ == "__main__":
    main()

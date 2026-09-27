"""Service tests for live reports changing graph and shelter decisions."""
from geoalchemy2.shape import from_shape
import networkx as nx
from shapely.geometry import LineString, Point, Polygon

from app.models import Area, RoadSegment, Shelter
from app.services import routing, site_ranking


class Scalars:
    def __init__(self, rows): self.rows = rows
    def __iter__(self): return iter(self.rows)


class Session:
    def __init__(self, roads=(), shelters=()): self.roads, self.shelters = roads, shelters
    def scalars(self, statement):
        # Service queries road and shelter tables independently.
        return Scalars(self.roads if "road_segments" in str(statement) else self.shelters)


def line(identifier, start, end):
    return RoadSegment(id=identifier, geometry=from_shape(LineString([start, end]), srid=4326), length_km=1.0, passes_hazard_zone=False)


def test_unsafe_mid_route_segment_causes_different_safe_path(monkeypatch):
    # A-B-C is shortest. A-D-C is the safe detour once B-C flips unsafe.
    roads = [line(1, (0, 0), (1, 0)), line(2, (1, 0), (2, 0)), line(3, (0, 0), (1, 1)), line(4, (1, 1), (2, 0))]
    session = Session(roads=roads)
    monkeypatch.setattr(routing, "unsafe_target_ids", lambda *_: set())
    original = routing.build_road_graph(session)
    original_path = nx.shortest_path(original, (0.0, 0.0), (2.0, 0.0), weight="weight")
    assert original_path == [(0.0, 0.0), (1.0, 0.0), (2.0, 0.0)]
    monkeypatch.setattr(routing, "unsafe_target_ids", lambda *_: {2})
    live = routing.build_road_graph(session)
    assert live[(1.0, 0.0)][(2.0, 0.0)]["weight"] > routing.HAZARD_EDGE_PENALTY_KM
    assert nx.shortest_path(live, (0.0, 0.0), (2.0, 0.0), weight="weight") == [(0.0, 0.0), (1.0, 1.0), (2.0, 0.0)]


def test_unsafe_shelter_is_excluded_from_recommendations(monkeypatch):
    area = Area(id=1, name="Area", geometry=from_shape(Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]), srid=4326), population=10, elderly_pct=1, children_pct=1, historical_disaster_count=0)
    unsafe = Shelter(id=1, name="Unsafe", geometry=from_shape(Point(.5, .5), srid=4326), capacity=100, medical_facility=True, water_available=True, road_accessible=True)
    safe = Shelter(id=2, name="Safe", geometry=from_shape(Point(2, 2), srid=4326), capacity=100, medical_facility=True, water_available=True, road_accessible=True)
    monkeypatch.setattr(site_ranking, "unsafe_target_ids", lambda *_: {1})
    results = site_ranking.rank_shelters(Session(shelters=[unsafe, safe]), area)
    assert [item.shelter.id for item in results] == [2]

"""NetworkX road routing with a strong penalty for hazardous segments."""
from dataclasses import dataclass
from math import ceil

import networkx as nx
from geoalchemy2.shape import to_shape
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import RoadSegment, Shelter
from app.services.safety_status import unsafe_target_ids

HAZARD_EDGE_PENALTY_KM = 1_000.0
AVERAGE_SPEED_KMH = 40.0


@dataclass(frozen=True)
class ComputedRoute:
    distance_km: float
    eta_minutes: int
    passes_hazard_zone: bool
    coordinates: list[list[float]]


def _node(coordinate) -> tuple[float, float]:
    return (round(float(coordinate[0]), 7), round(float(coordinate[1]), 7))


def build_road_graph(session: Session) -> nx.Graph:
    """Use segment endpoints as nodes and penalized distance as path weight."""
    graph = nx.Graph()
    unsafe_segments = unsafe_target_ids(session, "road_segment")
    for segment in session.scalars(select(RoadSegment)):
        line = to_shape(segment.geometry)
        start, end = _node(line.coords[0]), _node(line.coords[-1])
        live_unsafe = segment.id in unsafe_segments
        edge = {"segment_id": segment.id, "length_km": float(segment.length_km), "passes_hazard_zone": segment.passes_hazard_zone or live_unsafe, "weight": float(segment.length_km) + (HAZARD_EDGE_PENALTY_KM if segment.passes_hazard_zone or live_unsafe else 0)}
        # A simple Graph permits one edge per endpoint pair. Preserve the
        # cheapest one instead of letting database row order overwrite a safe
        # segment with a hazardous parallel segment.
        if not graph.has_edge(start, end) or edge["weight"] < graph[start][end]["weight"]:
            graph.add_edge(start, end, **edge)
    return graph


def _nearest_node(graph: nx.Graph, point) -> tuple[float, float]:
    if not graph.nodes:
        raise ValueError("Road network is empty")
    return min(graph.nodes, key=lambda node: (node[0] - point.x) ** 2 + (node[1] - point.y) ** 2)


def compute_safe_route(session: Session, from_geometry, to_geometry) -> ComputedRoute:
    graph = build_road_graph(session)
    start = _nearest_node(graph, to_shape(from_geometry).centroid)
    end = _nearest_node(graph, to_shape(to_geometry).centroid)
    try:
        nodes = nx.shortest_path(graph, start, end, weight="weight")
    except nx.NetworkXNoPath as exc:
        raise ValueError("No route connects the requested locations") from exc
    edges = [graph[nodes[index]][nodes[index + 1]] for index in range(len(nodes) - 1)]
    distance_km = round(sum(edge["length_km"] for edge in edges), 2)
    passes_hazard_zone = any(edge["passes_hazard_zone"] for edge in edges)
    coordinates = [[lon, lat] for lon, lat in nodes]
    if len(coordinates) == 1:
        coordinates.append(coordinates[0])
    return ComputedRoute(distance_km=distance_km, eta_minutes=ceil(distance_km / AVERAGE_SPEED_KMH * 60), passes_hazard_zone=passes_hazard_zone, coordinates=coordinates)


def recompute_route_from_position(session: Session, current_lat: float, current_lng: float, shelter_id: int) -> ComputedRoute:
    """Snap a live device position to the road graph and route to a safe shelter."""
    shelter = session.get(Shelter, shelter_id)
    if shelter is None:
        raise ValueError("Shelter not found")
    graph = build_road_graph(session)
    start = min(graph.nodes, key=lambda node: (node[0] - current_lng) ** 2 + (node[1] - current_lat) ** 2) if graph.nodes else None
    if start is None:
        raise ValueError("Road network is empty")
    end = _nearest_node(graph, to_shape(shelter.geometry).centroid)
    try:
        nodes = nx.shortest_path(graph, start, end, weight="weight")
    except nx.NetworkXNoPath as exc:
        raise ValueError("No safe route connects the current position to this shelter") from exc
    edges = [graph[nodes[index]][nodes[index + 1]] for index in range(len(nodes) - 1)]
    distance_km = round(sum(edge["length_km"] for edge in edges), 2)
    coordinates = [[lon, lat] for lon, lat in nodes] or [[current_lng, current_lat]]
    if len(coordinates) == 1: coordinates.append(coordinates[0])
    return ComputedRoute(distance_km=distance_km, eta_minutes=ceil(distance_km / AVERAGE_SPEED_KMH * 60), passes_hazard_zone=any(edge["passes_hazard_zone"] for edge in edges), coordinates=coordinates)

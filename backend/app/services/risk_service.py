"""GeoPandas read models backed by the transparent RiskEngine."""
import geopandas as gpd
from sqlalchemy import text
from sqlalchemy.engine import Engine
from app.services.risk_engine import RiskEngine


def load_risk_zone_features(engine: Engine, risk_engine: RiskEngine | None = None, intensity_multipliers: dict[str, float] | None = None) -> list[dict]:
    """Build GeoJSON features from Areas intersected with HazardLayers.

    GeoPandas performs the spatial join, while RiskEngine scores each area.
    """
    with engine.connect() as connection:
        areas = gpd.read_postgis(text("SELECT id, name, population, elderly_pct, children_pct, historical_disaster_count, geometry FROM areas"), connection, geom_col="geometry")
        hazards = gpd.read_postgis(text("SELECT id, hazard_type, intensity, geometry FROM hazard_layers"), connection, geom_col="geometry")
    if areas.empty:
        return []
    # EPSG:6933 is an equal-area CRS, allowing meaningful km² density values.
    areas["area_sq_km"] = areas.to_crs("EPSG:6933").geometry.area / 1_000_000
    areas["population_density"] = areas["population"] / areas["area_sq_km"].clip(lower=0.000001)
    max_population_density = float(areas["population_density"].max())
    max_historical_disaster_count = int(areas["historical_disaster_count"].max())
    if hazards.empty:
        joined = areas.copy()
        joined["hazard_type"] = "none"
        joined["intensity"] = 0.0
    else:
        # One area may touch several layers; retain the highest-intensity one.
        joined = gpd.sjoin(areas, hazards[["hazard_type", "intensity", "geometry"]], how="left", predicate="intersects")
        joined["intensity"] = joined["intensity"].fillna(0.0)
        joined["hazard_type"] = joined["hazard_type"].fillna("none")
        # Simulation supplies multipliers here; this GeoDataFrame is detached
        # from SQLAlchemy, so no HazardLayer row can be mutated or persisted.
        if intensity_multipliers:
            joined["intensity"] = joined.apply(lambda row: row["intensity"] * intensity_multipliers.get(row["hazard_type"], 1.0), axis=1)
        joined = joined.sort_values("intensity", ascending=False).drop_duplicates("id")

    scorer = risk_engine or RiskEngine()
    features: list[dict] = []
    for _, area in joined.iterrows():
        result = scorer.score(hazard_intensity=area["intensity"], population_density=area["population_density"], elderly_pct=area["elderly_pct"], children_pct=area["children_pct"], historical_disaster_count=area["historical_disaster_count"], max_population_density=max_population_density, max_historical_disaster_count=max_historical_disaster_count)
        features.append({"type": "Feature", "geometry": area["geometry"].__geo_interface__, "properties": {"area_id": str(area["id"]), "risk_score": result.score, "hazard": area["hazard_type"], "population": int(area["population"]), "vulnerability": result.vulnerability, "priority": result.priority, "breakdown": result.breakdown, "_area_name": area["name"]}})
    return features


def load_risk_for_location(engine: Engine, location: str) -> dict | None:
    """Locate an ID or case-insensitive area name within the scored district."""
    for feature in load_risk_zone_features(engine):
        properties = feature["properties"]
        if properties["area_id"] == location or properties["_area_name"].casefold() == location.casefold():
            return properties
    return None

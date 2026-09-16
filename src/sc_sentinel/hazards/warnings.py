"""Non-official analytical warning polygons derived from cell footprints."""
from __future__ import annotations
from sc_sentinel.radar.geometry import destination_latlon

LEVEL_RANK = {"NOT_ASSESSED": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3}

def warning_features(cells: list[dict], easting_m, northing_m, radar_lat: float, radar_lon: float) -> list[dict]:
    features = []
    for cell in cells:
        hazards = cell.get("hazards", {})
        strongest = max((item.get("level", "NOT_ASSESSED") for item in hazards.values()), key=lambda x: LEVEL_RANK.get(x, 0))
        if LEVEL_RANK.get(strongest, 0) < LEVEL_RANK["MEDIUM"]:
            continue
        x0, y0, x1, y1 = cell["bbox_grid"]
        corners = [(easting_m[x0], northing_m[y0]), (easting_m[x1], northing_m[y0]), (easting_m[x1], northing_m[y1]), (easting_m[x0], northing_m[y1])]
        coordinates = []
        for east, north in corners:
            distance = (east**2 + north**2) ** .5
            bearing = (90 if north == 0 else __import__('math').degrees(__import__('math').atan2(east, north))) % 360
            lat, lon = destination_latlon(radar_lat, radar_lon, bearing, distance)
            coordinates.append([lon, lat])
        coordinates.append(coordinates[0])
        features.append({"type": "Feature", "properties": {"cell_id": cell.get("track_id", f"component_{cell['component_id']}"), "timestamp_token": cell.get("timestamp_token"), "overall_alert_level": strongest, "disclaimer": "Automated analytical polygon; not an official meteorological warning."}, "geometry": {"type": "Polygon", "coordinates": [coordinates]}})
    return features

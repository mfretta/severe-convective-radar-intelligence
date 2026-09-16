"""Conservative assignment of radar cells between consecutive scans."""
from __future__ import annotations
from datetime import datetime
import math
from scipy.optimize import linear_sum_assignment


def _time(token: str) -> datetime:
    return datetime.strptime(token[:14], "%Y%m%d%H%M%S")


def track_pair(previous: dict, current: dict, maximum_speed_kmh: float = 150, max_intensity_difference_dbz: float = 25) -> list[dict]:
    """Return current-cell assignments; forbidden pairs are never matched."""
    old, new = previous.get("cells", []), current.get("cells", [])
    if not new:
        return []
    if not old:
        return [{"component_id": cell["component_id"], "track_id": f"{current['timestamp_token']}_C{cell['component_id']:03d}", "state": "new"} for cell in new]
    minutes = max((_time(current["timestamp_token"]) - _time(previous["timestamp_token"])).total_seconds() / 60, 1)
    maximum_distance_km = maximum_speed_kmh * minutes / 60
    cost = [[1e9 for _ in new] for _ in old]
    for i, left in enumerate(old):
        for j, right in enumerate(new):
            dx = (left["centroid_grid_x"] - right["centroid_grid_x"]) * 2 # current CAPPI grid is 2 km
            dy = (left["centroid_grid_y"] - right["centroid_grid_y"]) * 2
            distance = math.hypot(dx, dy)
            intensity_delta = abs(left["max_dbzh"] - right["max_dbzh"])
            if distance <= maximum_distance_km and intensity_delta <= max_intensity_difference_dbz:
                cost[i][j] = distance + intensity_delta / max_intensity_difference_dbz
    rows, cols = linear_sum_assignment(cost)
    matched = {col: row for row, col in zip(rows, cols) if cost[row][col] < 1e9}
    result = []
    for j, cell in enumerate(new):
        if j in matched:
            parent = old[matched[j]]
            result.append({"component_id": cell["component_id"], "track_id": parent.get("track_id", f"{previous['timestamp_token']}_C{parent['component_id']:03d}"), "state": "matched", "distance_km": cost[matched[j]][j]})
        else:
            result.append({"component_id": cell["component_id"], "track_id": f"{current['timestamp_token']}_C{cell['component_id']:03d}", "state": "new"})
    return result

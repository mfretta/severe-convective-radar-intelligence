"""Radar beam geometry using a configurable effective Earth radius."""
from __future__ import annotations

import math

EARTH_RADIUS_M = 6_371_000.0


def beam_height_m(range_m: float, elevation_deg: float, radar_altitude_m: float, earth_radius_factor: float = 4 / 3) -> float:
    """Beam-centre altitude above mean sea level (Doviak-Zrnić geometry)."""
    if range_m < 0:
        raise ValueError("range_m must be non-negative")
    radius = EARTH_RADIUS_M * earth_radius_factor
    elevation = math.radians(elevation_deg)
    return math.sqrt(range_m**2 + radius**2 + 2 * range_m * radius * math.sin(elevation)) - radius + radar_altitude_m


def ground_distance_m(range_m: float, elevation_deg: float, earth_radius_factor: float = 4 / 3) -> float:
    radius = EARTH_RADIUS_M * earth_radius_factor
    elevation = math.radians(elevation_deg)
    return radius * math.asin(range_m * math.cos(elevation) / (radius + beam_height_m(range_m, elevation_deg, 0, earth_radius_factor)))


def destination_latlon(latitude_deg: float, longitude_deg: float, bearing_deg: float, distance_m: float) -> tuple[float, float]:
    """Spherical great-circle destination, adequate for radar-domain validation."""
    angular = distance_m / EARTH_RADIUS_M
    lat1, lon1, bearing = map(math.radians, (latitude_deg, longitude_deg, bearing_deg))
    lat2 = math.asin(math.sin(lat1) * math.cos(angular) + math.cos(lat1) * math.sin(angular) * math.cos(bearing))
    lon2 = lon1 + math.atan2(math.sin(bearing) * math.sin(angular) * math.cos(lat1), math.cos(angular) - math.sin(lat1) * math.sin(lat2))
    return math.degrees(lat2), ((math.degrees(lon2) + 540) % 360) - 180


def gate_geolocation(latitude_deg: float, longitude_deg: float, radar_altitude_m: float, range_m: float, azimuth_deg: float, elevation_deg: float, earth_radius_factor: float = 4 / 3) -> tuple[float, float, float]:
    height = beam_height_m(range_m, elevation_deg, radar_altitude_m, earth_radius_factor)
    distance = ground_distance_m(range_m, elevation_deg, earth_radius_factor)
    latitude, longitude = destination_latlon(latitude_deg, longitude_deg, azimuth_deg, distance)
    return latitude, longitude, height

"""Small, dependency-free Rainbow XML header reader.

This module deliberately reads only the XML preamble. Gate payload decoding is
delegated to xradar in the Silver stage; this prevents a hand-written binary
decoder from becoming the scientific source of truth.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import xml.etree.ElementTree as ET

HEADER_END = b"<!-- END XML -->"
NAME_PATTERN = re.compile(r"^(?P<stamp>\d{16})(?P<moment>.+)\.vol$", re.IGNORECASE)


class RainbowHeaderError(ValueError):
    """Raised if a source file does not contain a valid Rainbow XML preamble."""


@dataclass(frozen=True)
class RainbowHeader:
    path: Path
    timestamp_token: str
    moment_from_name: str
    rainbow_version: str | None
    site_id: str | None
    site_name: str | None
    latitude_deg: float | None
    longitude_deg: float | None
    altitude_m: float | None
    wavelength_m: float | None
    beamwidth_deg: float | None
    scan_name: str | None
    elevations_deg: tuple[float, ...]
    range_step_km: float | None
    azimuth_counts: tuple[int, ...]
    bin_counts: tuple[int, ...]
    nyquist_velocity_ms: tuple[float, ...]
    native_moment: str | None


def _float(value: str | None) -> float | None:
    try:
        return float(value) if value not in (None, "") else None
    except ValueError:
        return None


def _int(value: str | None) -> int | None:
    try:
        return int(value) if value not in (None, "") else None
    except ValueError:
        return None


def _find_text(element: ET.Element, *names: str) -> str | None:
    wanted = {name.lower() for name in names}
    for child in element.iter():
        if child.tag.rsplit("}", 1)[-1].lower() in wanted and child.text:
            return child.text.strip()
    return None


def _child_value(element: ET.Element, *names: str) -> str | None:
    """Read a direct child value stored as either text or an attribute."""
    wanted = {name.lower() for name in names}
    for child in element:
        if child.tag.rsplit("}", 1)[-1].lower() in wanted:
            return (child.text or "").strip() or _attr(child, "value", "min", "max")
    return None


def _attr(element: ET.Element, *names: str) -> str | None:
    wanted = {name.lower() for name in names}
    for key, value in element.attrib.items():
        if key.lower() in wanted:
            return value
    return None


def read_rainbow_header(path: str | Path) -> RainbowHeader:
    path = Path(path)
    match = NAME_PATTERN.match(path.name)
    if not match:
        raise RainbowHeaderError(f"Filename does not contain a Rainbow timestamp/moment: {path.name}")
    with path.open("rb") as handle:
        payload = handle.read(1_000_000)
    end = payload.find(HEADER_END)
    if end < 0:
        raise RainbowHeaderError(f"Rainbow XML end marker not found in first MiB: {path}")
    xml_bytes = payload[:end].lstrip(b"\xef\xbb\xbf\x00 \t\r\n")
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise RainbowHeaderError(f"Cannot parse Rainbow XML: {path}") from exc

    # Rainbow headers carry metadata in element attributes, which is why all
    # lookups are attribute-based and intentionally tolerant of minor versions.
    def first_attr(*names: str) -> str | None:
        for element in root.iter():
            value = _attr(element, *names)
            if value is not None:
                return value
        return None

    slices = [el for el in root.iter() if el.tag.rsplit("}", 1)[-1].lower() == "slice"]
    elevations = tuple(v for el in slices if (v := _float(_child_value(el, "posangle", "elevation", "angle"))) is not None)
    azimuths: list[int] = []
    bins: list[int] = []
    nyquists: list[float] = []
    native_moment = None
    for slice_element in slices:
        for el in slice_element.iter():
            tag = el.tag.rsplit("}", 1)[-1].lower()
            if tag in {"dynv", "nyquist"}:
                value = _float(_attr(el, "value", "nyquist", "max", "maxvalue"))
                if value is not None:
                    nyquists.append(abs(value))
            if tag == "rawdata":
                rays = _int(_attr(el, "rays", "raycount"))
                bin_count = _int(_attr(el, "bins", "bincount"))
                if rays is not None:
                    azimuths.append(rays)
                if bin_count is not None:
                    bins.append(bin_count)
                native_moment = native_moment or _attr(el, "type")
    sensor = next((el for el in root.iter() if el.tag.rsplit("}", 1)[-1].lower() == "sensorinfo"), None)
    sensor_attr = lambda *names: _attr(sensor, *names) if sensor is not None else None
    sensor_text = lambda *names: _find_text(sensor, *names) if sensor is not None else None
    return RainbowHeader(
        path=path,
        timestamp_token=match.group("stamp"),
        moment_from_name=match.group("moment"),
        rainbow_version=_attr(root, "version"),
        site_id=sensor_attr("id", "siteid") or first_attr("siteid"),
        site_name=sensor_attr("name", "sitename"),
        latitude_deg=_float(sensor_text("lat", "latitude")),
        longitude_deg=_float(sensor_text("lon", "longitude")),
        altitude_m=_float(sensor_text("alt", "altitude", "height")),
        wavelength_m=_float(sensor_text("wavelen", "wavelength", "lambda")),
        beamwidth_deg=_float(sensor_text("beamwidth", "beamwidthdeg")),
        scan_name=first_attr("scanname", "name"),
        elevations_deg=elevations,
        range_step_km=_float(_find_text(root, "rangestep", "rscale")),
        azimuth_counts=tuple(azimuths),
        bin_counts=tuple(bins),
        nyquist_velocity_ms=tuple(nyquists),
        native_moment=native_moment,
    )

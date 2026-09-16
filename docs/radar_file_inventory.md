# Radar file inventory

## Scope and provenance

This inventory was generated directly from the XML preamble in every native Rainbow5 file under `2026-08-30/`. The binary gate payload has not been modified. Machine-readable provenance is in `data/metadata/radar_inventory.json`.

| Property | Verified value |
|---|---|
| Native file count | 2,045 `.vol` files |
| Timestamp groups | 233 |
| Archive time range | 2026-08-30 00:42:04–23:54:04 UTC (filename timestamps) |
| Radar site ID | CHP |
| Radar name | Radar do Oeste |
| Site coordinates | 27.048790°S, 52.603740°W |
| Site altitude | 822.0 m |
| Wavelength | 0.10417 m |
| Beamwidth | 1.0° |
| Scan strategy | `Optimised` (native header) |
| Actual sweep count | 14 |
| Elevations | 0.5, 0.9, 1.3, 1.8, 2.4, 3.1, 4.0, 5.1, 6.4, 8.0, 10.0, 12.5, 15.6, 19.5° |
| Azimuths | 360 rays per sweep |
| Gate spacing | 0.25 km |
| Range bins | 960 (0.5–4.0°), 728 (5.1–6.4°), 499 (8.0–19.5°) in representative KDP volume |
| Nyquist-like native `dynv` maxima | 31.251, 20.834, 29.9489 m/s by sweep group |

## Native moment files

The archive stores separate full-volume files by moment, so a timestamp should be treated as a group of available moment volumes rather than a single multi-moment file.

| Filename moment | File count |
|---|---:|
| `dBZ` | 228 |
| `dBuZ` | 225 |
| `ZDR` | 224 |
| `KDP` | 231 |
| `RhoHV` | 230 |
| `PhiDP` | 228 |
| `uPhiDP` | 226 |
| `V` | 228 |
| `W` | 225 |

`KDP` is an explicitly native `<rawdata type="KDP">` field. It will not be recomputed from `PhiDP` unless a separate, documented experimental product is requested.

## Important interpretation notes

- The internal scan filename includes `11ele`, but the XML contains 14 `<slice>` elements. SC Sentinel uses the decoded slice count, never the filename, for geometry.
- Nyquist velocity varies by sweep. It will be stored per sweep and raw velocity will always be preserved.
- The inventory establishes availability and metadata only. It does not yet assert that binary gates were decoded or that a radar moment passed QC.

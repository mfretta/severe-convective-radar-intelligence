# Severe Convective Radar Intelligence

## Archived Rainbow Radar Data Platform

Severe Convective Radar Intelligence processes archived native Rainbow5 radar observations from Radar do Oeste, Chapecó, Santa Catarina, Brazil. It preserves each source file, extracts the metadata actually encoded in the archive, and provides an auditable pipeline for quality-controlled radar products, storm objects, heuristic hazard guidance, and operational serving.

The archive is the source of truth. Values not present in a Rainbow header are represented as missing/configurable; they are never silently invented. Automated hazard outputs are analytical guidance, not official meteorological warnings or tornado confirmation.

### Verified archive facts

- 2,045 native `.vol` files in a one-day archive (2026-08-30)
- 233 timestamp groups, 00:42:04–23:54:04 UTC
- Native per-moment Rainbow5 volumes: `dBZ`, `dBuZ`, `ZDR`, `KDP`, `RhoHV`, `PhiDP`, `uPhiDP`, `V`, `W`
- 14 decoded elevation slices; the embedded scan filename is not used as a sweep-count authority
- Native KDP exists, so it will not be derived by default

### Architecture

![Severe Convective Radar Intelligence medallion architecture](docs/assets/severe-convective-radar-intelligence-architecture.png)

### Operational dashboard

### Radar replay video

[![Watch the 21:00–23:54 UTC radar replay](docs/video/replay-preview.png)](https://github.com/mfretta/severe-convective-radar-intelligence/raw/refs/heads/main/docs/video/Radar_Replay_2100-2354_UTC.mp4)

[Download MP4](docs/video/Radar_Replay_2100-2354_UTC.mp4) · [Watch on the project site](https://severe-convective-radar-intelligence.murilofretta.chatgpt.site/#replay) · [Download PowerPoint with embedded video](docs/presentation/Severe_Convective_Radar_Intelligence.pptx)

1080p replay at 1.5× playback speed, approximately 35 seconds. Includes 25 available scans from 21:00 to 23:54 UTC on 30 August 2026, with real 2 km CAPPI, cell footprints, recent tracks and scan-specific threshold colours. Observation timestamps retain gaps in the archive. The Sites showcase currently requires owner access.

### Dashboard screenshots

The archived replay presents the real 2 km DBZH CAPPI over the supplied Santa Catarina boundaries, detected cell footprints, recent cell tracks, and scan-specific threshold bands.

![Radar replay showing high-reflectivity cell footprints and tracked cells](docs/assets/Platform.png)

*Cell footprints and tracks during an active high-reflectivity scan.*

![Radar replay showing evolving convective cells and dynamic thresholds](docs/assets/Platform2.png)

*A later replay frame showing the evolving cell field and dynamic intensity bands.*

The first executable stage is the metadata inventory:

```powershell
python scripts/inspect_radar.py
python -m unittest discover -s tests -v
```

See [the file inventory](docs/radar_file_inventory.md) for provenance and verified scan facts.

### Run the validated vertical slice

```powershell
make inventory
make bronze
make quality
make silver
make cappi
make cells
make track
make hazards
make warnings
make validate
```

Serve the API with `make api`; build the React/Three.js client with `cd frontend; npm.cmd run build`.

### Data model and products

- **Bronze**: immutable, SHA-256 verified copies of every native `.vol` file.
- **Silver**: sweep-aware, ragged-range Zarr groups decoded by xradar. Raw velocity remains preserved.
- **Gold**: coverage-aware CAPPI, configurable reflectivity cells, tracks, heuristic hazard records, and GeoJSON analytical polygons.
- **Serving**: FastAPI exposes metadata, scans, volumes, CAPPI metadata, cells, tracks, warnings, and archived replay status.

### Method and limitations

Radar gates are georeferenced using configurable effective-Earth-radius beam geometry. CAPPI uses only beams within its declared height tolerance, and each product records coverage. Cell segmentation and all hazard thresholds are configurable. See [limitations](docs/limitations.md) before interpreting output.

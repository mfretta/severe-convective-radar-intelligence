## Slide 1

Introduce the project as an engineering case study using real archived weather-radar observations. The interface replays historical timestamps; it is not a live operational warning service. Explain the goal: turn complex sensor files into inspectable cells and trajectories with traceable processing.

## Slide 2

The archive contains separate moment volumes, rather than one tidy table per scan. Available moments include reflectivity, differential reflectivity, native KDP, correlation coefficient, differential phase, velocity and spectrum width. Field availability does not imply every moment contributes to the current tracking algorithm. The current cell path uses DBZH.

## Slide 3

Walk from left to right: preserve Rainbow source files in Bronze; decode sweep-aware Zarr groups and check quality; derive coverage-aware 2 km CAPPI, cells and tracks in Gold; serve products with FastAPI and the React dashboard. The illustration is conceptual: CAPPI products are stored under Gold in the current repository. Hazard scores and analytical polygons are heuristic products. The current dashboard is a 2D image and SVG view, not a validated 3D product.

## Slide 4

Explain the difference between software validity and scientific validity. Parsing successfully does not guarantee correct geometry, units or coverage. Preserve gaps and exclusions rather than implying complete observations. These are implemented controls and checks, not a claim of comprehensive clutter removal, attenuation correction or independently verified forecast skill.

## Slide 5

The altitude is 2 km above sea level, while the Cartesian grid spacing is also 2 km. Four connected grid pixels meet the 16 km² minimum area. Connectivity includes diagonals. Association uses actual elapsed time between scans. Current limitations include simple one-to-one association and no mature split/merge model. The tail is capped at 12 points, which is not exactly one hour because archive cadence and gaps vary. The side legend classifies detected cells by peak DBZH; weaker echoes remain visible in the raster.

## Slide 6

Use this screenshot to walk through the actual interface: supplied municipal and country boundaries, the real 2 km CAPPI, outlined cell footprints and trajectories, the scan-specific side legend, and the cell table. Replay changes presentation timing while retaining observation timestamps. The screenshot includes heuristic heavy-rain and hail fields and rotation marked NOT_ASSESSED. Explain that display projection and physical validation remain improvement areas.

## Slide 7

The local archive checkpoint reports 217 processed timestamps, 16 exclusions and 2127 track-point records. These measure engineering throughput and available products, not recall, false-alarm rate or confirmed storm severity. Review exclusion reasons in the archive manifest. Independent event truth and quantitative skill evaluation remain future work.

## Slide 8

Close by connecting the work to data engineering: provenance, reproducible processing, explicit quality and understandable outputs. The project is an analytical prototype based on archived data. Rain and hail scores are heuristic; rotation is not assessed. Invite questions about design decisions and point to the GitHub repository. Suggested presentation length: eight to ten minutes.
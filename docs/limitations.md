# Scientific and operational limitations

SC Sentinel is an archived-radar analytical platform, not an official warning system.

- Rainbow moments are decoded from the source files and native KDP is retained; native data are never overwritten.
- CAPPI is a nearest-valid-beam diagnostic. Its coverage mask is mandatory and uncovered cells are not extrapolated.
- Reflectivity segmentation identifies configurable candidate cells. It does not prove convection type or surface impact.
- Heavy-rain output is **potential**, not quantitative precipitation estimation: no local Z-R or KDP-R calibration has been applied.
- Hail output is **potential**. In the current product it is capped without validated echo-top/freezing-level evidence.
- Rotation is `NOT_ASSESSED` until velocity dealiasing, coherent couplet/shear analysis, and multi-scan persistence checks are implemented and validated.
- Automated polygons are analytical footprints, not official meteorological warnings.
- The provided archive is historical. Replay changes presentation timing only; it never modifies observation timestamps.

The current production-ready vertical slice is the verified two-scan path: native archive → Bronze → Silver → QC → CAPPI → cells → tracking → heuristic guidance → GeoJSON/API/frontend build.

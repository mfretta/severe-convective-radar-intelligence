.PHONY: inventory bronze quality silver cappi cells track hazards warnings validate api frontend test

inventory:
	python scripts/inspect_radar.py
bronze:
	python scripts/stage_bronze.py
quality:
	python scripts/assess_quality.py
silver:
	python scripts/decode_silver.py 2026083023540400
cappi:
	python scripts/generate_cappi.py 2026083023540400
cells:
	python scripts/segment_cells.py 2026083023540400
track:
	python scripts/track_cells.py 2026083023480400 2026083023540400
hazards:
	python scripts/score_hazards.py 2026083023540400
warnings:
	python scripts/generate_warnings.py 2026083023540400
validate:
	python scripts/validate_project.py
api:
	uvicorn backend.app.main:app --reload
frontend:
	cd frontend && npm.cmd run dev
test:
	python -m unittest discover -s tests -v

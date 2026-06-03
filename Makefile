.PHONY: fetch preprocess render watch serve run test

fetch:
	mkdir -p data
	uv run python scripts/fetch.py data/incidents_raw.json

preprocess:
	uv run python scripts/preprocess.py data/incidents_raw.json data/incidents.json

render:
	mkdir -p web
	uv run python scripts/render.py data/incidents.json web/index.html

run:
	uv run python run.py

test:
	uv run python -m unittest discover -s tests

watch:
	uv run python -m scripts.watch

serve:
	cd web && npx serve

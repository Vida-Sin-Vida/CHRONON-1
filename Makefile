install:
	python -m pip install -e ".[dev]"

test:
	pytest -q

reproduce:
	chronon1 reproduce --config configs/toy.yml

lint:
	ruff check .

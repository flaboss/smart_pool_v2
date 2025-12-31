.PHONY: venv run

make venv:
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip setuptools wheel
	. venv/bin/activate && pip install -e ".[dev]"

make run:
	. venv/bin/activate && flet run main.py

make web:
	. venv/bin/activate && flet run --web main.py

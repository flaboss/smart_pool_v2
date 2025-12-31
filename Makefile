VENV_DIR = .venv
PYTHON = $(VENV_DIR)/bin/python

.PHONY: venv run web lint

venv:
	python3 -m venv $(VENV_DIR)
	. $(VENV_DIR)/bin/activate && pip install --upgrade pip setuptools wheel
	. $(VENV_DIR)/bin/activate && pip install .

run:
	. $(VENV_DIR)/bin/activate && flet run main.py

web:
	. $(VENV_DIR)/bin/activate && flet run --web main.py

lint:
	. $(VENV_DIR)/bin/activate && ruff check .

format:
	. $(VENV_DIR)/bin/activate && ruff format .

build_apk:
	. $(VENV_DIR)/bin/activate && flet build apk

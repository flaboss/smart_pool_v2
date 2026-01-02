VENV_DIR = .venv
PYTHON = $(VENV_DIR)/bin/python

.PHONY: venv run web lint
 
help: ## Displays the available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

venv:
	python3 -m venv $(VENV_DIR)
	. $(VENV_DIR)/bin/activate && pip install --upgrade pip setuptools wheel
	. $(VENV_DIR)/bin/activate && pip install .

run:
	. $(VENV_DIR)/bin/activate && flet run main.py

web:
	. $(VENV_DIR)/bin/activate && flet run --web main.py

clean: ## RRemoves temp files
	## rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.py[co]" -delete

lint:
	. $(VENV_DIR)/bin/activate && ruff check .

format:
	. $(VENV_DIR)/bin/activate && ruff format .

build_apk:
	. $(VENV_DIR)/bin/activate && flet build apk

install_apk:
	cp build/apk/app-release.apk ~/apks/smart_pool.apk
	adb install -r ~/apks/smart_pool.apk

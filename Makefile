.PHONY: setup install seed run test clean

VENV := venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

# Default setup: create venv, install deps, and seed db
setup: $(VENV)/bin/activate install seed

$(VENV)/bin/activate:
	python3 -m venv $(VENV)

install: $(VENV)/bin/activate
	$(PIP) install -r requirements.txt

seed: $(VENV)/bin/activate
	$(PYTHON) seed.py

run: $(VENV)/bin/activate
	$(PYTHON) server.py

test: $(VENV)/bin/activate
	$(PYTHON) -m unittest test_server.py

clean:
	rm -rf $(VENV)
	rm -rf __pycache__
	rm -f test.db
	rm -f *.pyc

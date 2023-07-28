SHELL := /bin/bash
run:
	python automation.py
venv:
	python3 -m venv .venv && chmod +x .venv/bin/activate

setup: requirements.txt
	pip install -r requirements.txt
clean:
	rm -rf __pycache__
deactivate:
	deactivate
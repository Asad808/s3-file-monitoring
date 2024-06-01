install:
	python -m venv venv
	. venv/bin/activate; pip install -r requirements.txt

run:
	. venv/bin/activate; python monitor.py

all: install run

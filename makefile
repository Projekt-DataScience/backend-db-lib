install:
	pip install -r requirements.txt

debug: install
	python3 app/manager.py
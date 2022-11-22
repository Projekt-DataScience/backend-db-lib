export ALGORITHM="HS256"
export SECRET="feaf1952d59f883ecf260a8683fed21ab0ad9a53323eca4f"
export DATABASE_URL="postgresql://backendgang:backendgang@db:8000"
install:
	pip install -r requirements.txt

debug: install
	python3 app/models.py
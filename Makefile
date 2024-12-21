build:
	poetry install

setup:
	poetry run alembic upgrade head

unittest:
	poetry run pytest tests

run:
	poetry run aidevsys_knowledge
run: 
	clear
	uvicorn main:app --host 0.0.0.0 --port 8001 --reload

migrate:
	alembic upgrade head

migrations:
	alembic revision --autogenerate -m "migration"
	
format:
	black .

lint:
	flake8 .

format-lint: format lint
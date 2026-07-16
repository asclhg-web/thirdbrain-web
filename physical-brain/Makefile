.PHONY: dev init test demo up

init:
	python3 -m graph.init_db
	python3 -m graph.seed
	python3 -m pipelines.mock_health --days 30

dev:
	python3 -m uvicorn server.main:app --host 0.0.0.0 --port 8800 --reload

test:
	python3 -m pytest tests/ -q

demo:
	python3 -m scripts.demo

up:
	docker compose up -d

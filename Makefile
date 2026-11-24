IMAGE ?= demo-api:local

.PHONY: install lint test run docker-build docker-run kind-deploy

install:
	pip install -r requirements-dev.txt

lint:
	ruff check .
	ruff format --check .

test:
	pytest -q

run:
	uvicorn app.main:app --reload --port 8080

docker-build:
	docker build -t $(IMAGE) .

docker-run:
	docker run --rm -p 8080:8080 $(IMAGE)

kind-deploy:
	./scripts/kind-deploy.sh

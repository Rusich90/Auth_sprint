.PHONY: dev pre-commit isort black mypy flake8 pylint lint

dev: pre-commit

pre-commit:
	pre-commit install
	pre-commit autoupdate

isort:
	isort . --profile black

black:
	black .

mypy:
	mypy -p app

flake8:
	flake8 .

pylint:
	pylint app

lint: isort black mypy flake8 pylint

.PHONY: test
test:
	docker-compose -f tests/docker-compose.yml down
	docker-compose -f tests/docker-compose.yml build
	docker-compose -f tests/docker-compose.yml up

.PHONY: test-cleanup
test-cleanup:
	docker-compose -f tests/docker-compose.yml down

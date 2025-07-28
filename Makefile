black:
	black src tests

ruff-check:
	ruff check src tests

ruff-format:
	ruff check src tests --fix

format: black ruff-format


audit:
	pip-audit

bandit:
	bandit -r . -x tests,migrations -ll

security-check: audit bandit


up:
	docker-compose up --remove-orphans --build \
		fitness-ledger-service \
		postgresql

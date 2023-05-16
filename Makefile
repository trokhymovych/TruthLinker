lint: ## Lint whole python project
	@echo "Run linter truthlinker and tests folders"
	flake8 truthlinker/ tests/
	isort --check-only --diff --stdout .
	mypy truthlinker/
	@echo "Done"

format: ## Format python code
	isort .

install: ## Create virtual environment and setup requirements
	@echo "Setup poetry virtual environment"
	poetry install
	@echo "Done"

activate_virtual_env: ## Activate virtual environment
	@echo "Activating poetry virtual environment"
	poetry shell
	@echo "Done"

test: ## Run test suit
	@echo "Running tests..."
	pytest tests --cov=truthlinker
	@echo "Done test run"

test_cov: ## Run test suit
	@echo "Running tests..."
	pytest tests --cov=truthlinker --cov-report=html
	@echo "Done test run"

ci_lint: ## Lint whole python package in CI runner
	poetry run flake8 truthlinker/ tests/
	poetry run isort --check-only --diff --stdout .
	poetry run mypy truthlinker/

ci_test: ## Lint whole python package in CI runner
	poetry run pytest tests/ --cov=truthlinker

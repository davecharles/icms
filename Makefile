.DEFAULT_GOAL := help

.EXPORT_ALL_VARIABLES:
DJANGO_SETTINGS_MODULE=config.settings.development

UID=$(shell id -u):$(shell id -g)

##@ Help
help: ## Show this screen
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
	@echo ""

##@ Development
migrations: ## make db migrations
	unset UID && \
	docker-compose run --rm web ./manage.py makemigrations ${OPTS}

migrate: ## execute db migration
	unset UID && \
	docker-compose run --rm web ./manage.py migrate


loaddata: ## Load fixtures
	unset UID && \
	docker-compose run --rm web ./manage.py loaddata --app web web/fixtures/web/*.json

dumpdata: ## dumps db data
	unset UID && \
	docker-compose run --rm web ./manage.py dumpdata --format=json web  > test.json

sqlsequencereset: ## Use this command to generate SQL which will fix cases where a sequence is out of sync with its automatically incremented field data
	unset UID && \
	docker-compose run --rm web ./manage.py sqlsequencereset web

createsuperuser: ## create django super user
	unset UID && \
	docker-compose run --rm web ./manage.py createsuperuser

clean: ## removes python cache files from project
	unset UID && \
	docker-compose run --rm web find . -type d -name __pycache__ -exec rm -rf {} \+

requirements: ## install dev and prod dependecies via pipenv
	unset UID && \
	docker-compose run --rm web python3 -m pipenv install --dev --system

fixlock: ## install prod dependencies via pipenv
	unset UID && \
	docker-compose run --rm web pipenv install

collectstatic: ## copies static files to STATIC_ROOT
	docker-compose run --rm web ./manage.py collectstatic --noinput --traceback

build: ## build docker containers
	docker-compose pull
	docker-compose build

shell: ## Starts the Python interactive interpreter
	unset UID && \
	docker-compose run --rm web ./manage.py shell

all: requirements

setup: ## sets up system for first use, you might want to run load data after
	mkdir -p pgdata
	chmod -R 777 pgdata
	make requirements migrations migrate


##@ Server
debug: ## runs sytem in debug mode
	ICMS_DEBUG=True \
	ICMS_MIGRATE=False \
	docker-compose up

run: ## Run with Gunicorn and Whitenoise serving static files
	unset UID && \
	ICMS_SECRET_KEY='prod' \
	DATABASE_URL='postgres://postgres@db:5432/postgres' \
	ICMS_ALLOWED_HOSTS='localhost' \
	ICMS_RECAPTCHA_PUBLIC_KEY='6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI' \
	ICMS_RECAPTCHA_PRIVATE_KEY='6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe' \
	ICMS_EMAIL_FROM='prod@example.com' \
	ICMS_ADDRESS_API_KEY='prod' \
	ICMS_SILENCED_SYSTEM_CHECKS='captcha.recaptcha_test_key_error' \
	AWS_ACCESS_KEY_ID='prod' \
	AWS_SECRET_ACCESS_KEY='prod' \
	ELASTIC_APM_ENVIRONMENT='prod-test' \
	DJANGO_SETTINGS_MODULE=config.settings.production \
	docker-compose up

down: ## Stops and downs containers
	docker-compose down

##@ Tests & Reports
test: clean ## run tests
	unset UID && \
	ICMS_DEBUG=False \
	TEST_TARGET='web/tests' \
	DJANGO_SETTINGS_MODULE=config.settings.test \
	docker-compose run --rm web pytest --verbose --cov=web --cov=config $(TEST_TARGET)

accessibility: ## Generate accessibility reports
	unset UID && \
	docker-compose run --rm pa11y node index.js

test_style: clean ## runs linter
	unset UID && \
	DJANGO_SETTINGS_MODULE=config.settings.test \
	docker-compose run --rm web pytest --flake8

##@ Releases

release_major: ## create major release
	./scripts/release.sh major

release_minor: ## create minor release
	./scripts/release.sh minor

release_patch: ## create patch release
	./scripts/release.sh patch


.PHONY: run check test clean celery isort

pyenv_position = $(shell whereis pyenv)

ifneq ($(pyenv_position), pyenv:)
	python_position = $(shell pyenv which python)
	python_version = $(shell python -V | awk -F ' ' '{print substr($$2,0,4)}')
	python_path = $(python_position)$(python_version)
endif

check:
	@echo 'Checking...'
ifneq ($(pyenv_position), pyenv:)
	@[ -f $(python_path) ] || (ln -s $(python_position) $(python_path) && echo 'Made symbolic link $(python_path)')
	@[ -d flask_api_project/instance ] || (echo 'Error: You must create an folder named instance at root of project.Then create flask_api_project/instance/__init__.py and flask_api_project/instance/secret.py.')
	@[ -f flask_api_project/instance/dev.py ] || (echo 'Error: You must create an file named flask_api_project/instance/dev.py')
	@[ -f .python-version ] || (echo 'Suggestion: You must give an file named .python-version if you use pyenv and virtualenv.')
	@echo 'Done [check]'
else
	@echo "Error: You should use pyenv. [https://github.com/pyenv/pyenv]"
endif

run:
	@flask_api_project run --debugger --reload --with-threads -h 0.0.0.0

clean:
	@echo 'removing...'
	@find . -name '.tox' -print -exec rm -rf {} +
	@find . -name 'dist' -print -exec rm -rf {} +
	@find . -name 'htmlcov' -print -exec rm -rf {} +
	@find . -name '*.pyc' -print -exec rm -f {} +
	@find . -name '*.pyo' -print -exec rm -f {} +
	@find . -name '*.log' -print -exec rm -f {} +
	@find . -name '.pytest_cache' -print -exec rm -rf {} +
	@find . -name '__pycache__' -print -exec rm -rf {} +
	@find . -name 'beat.*' -print -exec rm -rf {} +
	@find . -path ./.coveragerc -prune -o -name '*coverage*' -print -exec rm -f {} +
	@echo 'Done [clean]'

test: clean
	@tox

celery:
	@celery -B -A celery_worker.celery worker --loglevel=info -s ./flask_api_project/proj/schedule/beat

isort:
	@isort --order-by-type -rc -up -sp flask_api_project/*
	@isort --order-by-type -rc -up -sp tests/*
	@echo 'Done [isort]'

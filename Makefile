#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME = culvertvision
PYTHON_VERSION = 3.11
PYTHON_INTERPRETER = python
CONDA_BIN = mamba

#################################################################################
# COMMANDS                                                                      #
#################################################################################


## Install Python Dependencies
.PHONY: requirements
requirements:
	$(CONDA_BIN) env update --name $(PROJECT_NAME) --file environment.yml --prune
	



## Delete all compiled Python files
.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Lint using flake8 and black (use `make format` to do formatting)
.PHONY: lint
lint:
	flake8 culvertvision
	isort --check --diff --profile black culvertvision
	black --check --config pyproject.toml culvertvision

## Format source code with black
.PHONY: format
format:
	black --config pyproject.toml culvertvision




## Set up python interpreter environment
.PHONY: create_environment
create_environment:
	$(CONDA_BIN) env create --name $(PROJECT_NAME) -f environment.yml
	
	@echo ">>> $(CONDA_BIN) env created. Activate with:\$(CONDA_BIN) activate $(PROJECT_NAME)"
	



#################################################################################
# PROJECT RULES                                                                 #
#################################################################################


## Make Dataset
.PHONY: data
data: requirements
	$(PYTHON_INTERPRETER) culvertvision/data/make_dataset.py


#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys; \
lines = '\n'.join([line for line in sys.stdin]); \
matches = re.findall(r'\n## (.*)\n[\s\S]+?\n([a-zA-Z_-]+):', lines); \
print('Available rules:\n'); \
print('\n'.join(['{:25}{}'.format(*reversed(match)) for match in matches]))
endef
export PRINT_HELP_PYSCRIPT

help:
	@python -c "${PRINT_HELP_PYSCRIPT}" < $(MAKEFILE_LIST)

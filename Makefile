PACKAGE_PATH=BranchedGP
TEST_PATH=testing
TEST_REQUIREMENTS=test_requirements.txt
NOTEBOOK_PATH=notebooks

install:
	pip install -r $(TEST_REQUIREMENTS)


dev_install:
	pip install -e .


test:
	nosetests $(TEST_PATH)

jupyter_server:
	jupyter notebook $(NOTEBOOK_PATH)

freeze_requirements:
	pip freeze > $(TEST_REQUIREMENTS)


check_black:
	black --check .

check_isort:
	isort --diff .

check_format: check_black check_isort


isort:
	isort .

black:
	black .

format: isort black


lint:
	flake8 --max-line-length 120 $(TEST_PATH) $(PACKAGE_PATH)

mypy:
	mypy --ignore-missing-imports .

static_checks: mypy lint


all_checks: static_checks check_format test

PIP_REQUIRE_VIRTUALENV=true

.PHONY: init
init:
	pip install -r requirements/dev.txt

.PHONY: test
test:
	pytest

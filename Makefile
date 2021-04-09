VIRTUAL_ENV 	?= env

all: $(VIRTUAL_ENV)

$(VIRTUAL_ENV): setup.cfg
	@[ -d $(VIRTUAL_ENV) ] || python -m venv $(VIRTUAL_ENV)
	@$(VIRTUAL_ENV)/bin/pip install -e .[tests]
	@touch $(VIRTUAL_ENV)

VERSION	?= minor

.PHONY: version
version:
	pip install bump2version
	bump2version $(VERSION)
	git checkout master
	git pull
	git merge develop
	git checkout develop
	git push origin develop master
	git push --tags

.PHONY: minor
minor:
	make version VERSION=minor

.PHONY: patch
patch:
	make version VERSION=patch

.PHONY: major
major:
	make version VERSION=major


.PHONY: clean
# target: clean - Display callable targets
clean:
	rm -rf build/ dist/ docs/_build *.egg-info
	find $(CURDIR) -name "*.py[co]" -delete
	find $(CURDIR) -name "*.orig" -delete
	find $(CURDIR)/$(MODULE) -name "__pycache__" | xargs rm -rf

.PHONY: upload
# target: upload - Upload module on PyPi
upload: clean
	@pip install twine wheel
	@python setup.py bdist_wheel
	@twine upload dist/*


test t: $(VIRTUAL_ENV)
	$(VIRTUAL_ENV)/bin/pytest tests.py


mypy: $(VIRTUAL_ENV)
	$(VIRTUAL_ENV)/bin/mypy asgi_prometheus


example: $(VIRTUAL_ENV)
	$(VIRTUAL_ENV)/bin/uvicorn --reload --port 5000 example:app

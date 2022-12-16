install:
	pip install -e .

install-dev:
	pip-sync

install-front:
	npm i

doc-serve:
	mkdocs serve

front:
	npm run grunt

lint:
	flake8 cp2k_basis cp2k_basis_webservice tests --max-line-length=120 --ignore=N802
	npm run grunt jshint

test:
	python -m unittest discover -s tests

run:
	flask --app cp2k_basis_webservice run
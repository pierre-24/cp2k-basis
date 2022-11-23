install:
	pip-sync

lint:
	flake8 cp2k_basis tests --max-line-length=120 --ignore=N802

test:
	python -m unittest discover -s tests

run:
	flask --app cp2k_basis_webservice run
install:
	pip-sync && pip3 install -e .

lint:
	flake8 cp2k_basis tests --max-line-length=120 --ignore=N802

test:
	python -m unittest discover -s tests
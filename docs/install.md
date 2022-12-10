# Install and contribute

## Install and run (simple version)

First, install node. It is recommended to use [`nvm`](https://github.com/nvm-sh/nvm#install--update-script) to do so.

Then:

```bash
# clone 
git clone https://github.com/pierre-24/cp2k-basis.git
cd cp2k-basis

# optional (but recommended): create virtualenv
python -m venv virtualenv
source venv/bin/activate

# install dependencies
make install
make install-front

# build front
make front

# run the webservice:
# either:
make run
# or,
flask --app cp2k_basis_webservice run
```

If you want to use your own library of basis and pseudopotentials, check out [this page](library_build.md), and then:

```bash
# create an instance folder
# see https://flask.palletsprojects.com/en/latest/config/#instance-folders
mkdir instance

# copy source
cp library/DATA_SOURCES.yml instance/

# after editing the DATA_SOURCES.yml file to fit your needs, 
# run the `cb_fetch_data` command to create a new library:
cb_fetch_data instance/DATA_SOURCES.yml -o instance/library.h5 

# setup a custom config
echo "LIBRARY='instance/library.h5'" > instance/settings.py
```

And then you can restart the webservice.

## Contribute

Contributions, either with [issues](https://github.com/pierre-24/cp2k-basis/issues) or [pull requests](https://github.com/pierre-24/cp2k-basis/pulls) are welcomed.

### Install

If you want to contribute, this is the usual deal: 
start by [forking](https://guides.github.com/activities/forking/), then clone your fork and use the following install procedure instead.

```bash
cd cp2k-basis

# definitely recommended in this case: use a virtualenv!
python -m venv virtualenv
source venv/bin/activate

# install also dev dependencies
pip install pip-tools
make install-dev
make install-front

# ... then build front and run (see above)
```

A useful setting is to setup the webservice to use the (smaller) test library for development:

```bash
mkdir instance
echo "LIBRARY='tests/LIBRARY_EXAMPLE.h5'" > instance/settings.py
```

The webservice should then be faster to start & reload.

### Contribute

Don't forget to work on a separate branch, and to run the linting and tests:

```bash
make lint  # flake8
make test  # unit tests
```

If you want to see and edit the doc, you can run the `mkdocs` webserver:

```bash
make doc-serve
```

Don't forget to edit the documentation if you modify something.
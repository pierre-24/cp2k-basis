# Install and contribute

## Install and run

```bash
# clone 
git clone https://github.com/pierre-24/cp2k-basis.git
cd cp2k-basis

# optional (but recommended): create virtualenv
python -m venv virtualenv
source venv/bin/activate

# install dependencies
make install

# run the webservice:
# either:
make run
# or,
flask --app cp2k_basis_webservice run
```

If you want to use your own library of basis and pseudopotentials,

```bash
# create an instance folder
# see https://flask.palletsprojects.com/en/latest/config/#instance-folders
mkdir instance

# copy source
cp DATA_SOURCES.yml instance/

# after editing the DATA_SOURCES.yml file to fit your needs, 
# run the `cp2k_basis_fetch_data` command to create a new library
cp2k_basis_fetch_data instance/DATA_SOURCES.yml -o instance/library.h5 

# setup a custom config
echo "LIBRARY='instance/library.h5'" > instance/settings.py
```

And then you can run the webservice.

## Contribute

Contributions, either with [issues](https://github.com/pierre-24/cp2k_basis/issues) or [pull requests](https://github.com/pierre-24/cp2k_basis/pulls) are welcomed.

If you can to contribute, this is the usual deal: 
start by [forking](https://guides.github.com/activities/forking/), then clone your fork and follow the installation instructions above.

Don't forget to work on a separate branch, and to run the linting and tests:

```bash
make lint  # flake8
make test  # unit tests
```

A useful setting is to setup the webservice to use the (smaller) test library for development:

```bash
mkdir instance
echo "LIBRARY='tests/LIBRARY_EXAMPLE.h5'" > instance/settings.py
```

The webservice should then be faster to start & reload.
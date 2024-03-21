# Install and contribute

## Install and run (simple version)

First, install node. **It is recommended to use [`nvm`](https://github.com/nvm-sh/nvm#install--update-script) to do so.**

Then, install the project and its dependencies:

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
```
 

Finally, build the library, as described on [this page](library_build.md):

```bash
# create an instance folder
# see https://flask.palletsprojects.com/en/latest/config/#instance-folders
mkdir instance

# run the `cb_fetch_data` command to create a new library:
cb_fetch_data library/DATA_SOURCES.yml -o instance/library.h5 
```

And then you can start the webservice:


```bash
# either:
make run
# or,
flask --app cp2k_basis_webservice run
```

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

### Tips to contribute

+ A useful setting is to setup the webservice to use the (smaller) test library for development:

    ```bash
    mkdir instance
    echo "LIBRARY='tests/LIBRARY_EXAMPLE.h5'" > instance/settings.py
    ```
    
    The webservice should then be faster to start & reload.

+ A good place to start is the [list of issues](https://github.com/pierre-24/cp2k-basis/issues).
  In fact, it is easier if you start by filling an issue, and if you want to work on it, says so there, so that everyone knows that the issue is handled.

+ Don't forget to work on a separate branch.
  Since this project follow the [git flow](http://nvie.com/posts/a-successful-git-branching-model/), you should base your branch on `dev`, not work in it directly:

    ```bash
    git checkout -b new_branch origin/dev
    ```
 
+ Don't forget to regularly run the linting and tests:

    ```bash
    make lint
    make test
    ```
    
    Indeed, the code follows the [PEP-8 style recommendations](http://legacy.python.org/dev/peps/pep-0008/), checked by [`flake8`](https://flake8.pycqa.org/en/latest/), for the python part and use [`jshint`](https://jshint.com/) for the JS part.
    Having an extensive test suite is also a good idea to prevent regressions.
  
+ If you modify the front (i.e., the JS script file or the stylesheet), don't forget to rebuild the front to see the effects:

    ```bash
    make front
    ```
  
    Indeed, both JS and SCSS are minified.

+ If you want to see and edit the doc, you can run the `mkdocs` webserver:

    ```bash
    make doc-serve
    ```

+ Pull requests should be unitary, and include unit test(s) and documentation if needed. 
  The test suite and lint must succeed for the merge request to be accepted.
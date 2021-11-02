Development
----------------------------

To develop dcodex, you should clone the latest version from github:

.. code-block:: bash

    git clone https://github.com/rbturnbull/dcodex.git
    cd dcodex

Then install the dependencies with poetry:

.. code-block:: bash

    poetry install
    poetry shell

If you don't have poetry installed, get it by looking at the instructions here: https://python-poetry.org/docs/#installation

You should then be able to run the tests:

.. code-block:: bash

    ./runtests.py

To check the testing coverage:

.. code-block:: bash

    coverage run ./runtests.py
    coverage report

To generate the documentation:

.. code-block:: bash

    sphinx-autobuild docs docs/_build/html --open-browser

If this clashes with a port that you're already running, then you can set a port manually with ``--port``.

Dependencies
============

The main two dependencies needed are python (version 3.8 or 3.9 at the time of writing) and PostgreSQL. You can install these on your system directly or you can run a dcodex project in Docker.

Mac
---

To install on a Mac, first you need ``gcc``. The easiest way to get this is to get the XCode Command Line Tools:

.. code-block:: bash

    xcode-select --install

Then you can install `Homebrew <https://brew.sh/>`_:

.. code-block:: bash

    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

Use Homebrew to install Python:

.. code-block:: bash

    brew install python

Confirm that you have Python 3.8 or 3.9 by doing:

.. code-block:: bash

    python3 --version

dcodex uses `Poetry <https://python-poetry.org>`_ to handle the Python dependencies. Install it using this command:

.. code-block:: bash

    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -


Now install and start `PostgreSQL <https://www.postgresql.org/>`_:

.. code-block:: bash

    brew install postgresql
    brew services start postgresql

Windows
-------

To install poetry, run this command in a Powershell:

.. code-block:: bash

    (Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py -UseBasicParsing).Content | python -

To install some of the dependencies, you will need to have Microsoft Visual Studio and C++ Build Tools (https://visualstudio.microsoft.com/vs/) installed on your system.

If you are setting up a dcodex project with dcodex-cookiecutter, make sure you enter ``y`` for the ``windows`` option.

Once you have created your dcodex project, enter the project directory.
If your default version of Python is 3.10 or later, you must ensure that poetry is using a virtual environment running version 3.8 or 3.9:

.. code-block:: bash
    poetry env use <path>\\<to>\\Python38\\python.exe

    poetry env use <path>\\<to>\\Python39\\python.exe

(If you have the typical installation of Python under your user account, then the first part of this path should be ``C:\Users\<you>\AppData\Local\Programs\Python\``.)

From here, you should be able to install the dependencies for your dcodex project via

.. code-block:: bash
    poetry install
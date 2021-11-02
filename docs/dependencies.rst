Dependencies
============

The main two dependencies needed are python (version 3.8 or later) and PostgreSQL. You can install these on your system directly or you can run a dcodex project in Docker.

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

Confirm that you have Python 3.8 or greater by doing:

.. code-block:: bash

    python --version

Now install and start `PostgreSQL <https://www.postgresql.org/>`_:

.. code-block:: bash

    brew install postgresql
    brew services start postgresql

Windows
-------

I haven't yet tried installing installing the dependencies on Windows. If you do, please consider writing some instructions and added them to this section of the documentation.
Installation
============================================


Package Installation
--------------------

To install dcodex into a Django project without using dcodex-cookiecutter, first install the module with pip:

.. code-block:: bash

    pip install git+https://github.com/rbturnbull/dcodex.git

Then add dcodex and its dependencies to your ``INSTALLED_APPS`` in your settings:

.. code-block:: python

    INSTALLED_APPS += [
        # dcodex dependencies
        "adminsortable2",
        'easy_thumbnails',
        'filer',
        'mptt',
        'imagedeck',
        # dcodex apps
        "dcodex",
    ]

See also the insallation instructions for other dcodex modules.
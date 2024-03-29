
<p align="center">
<img src="./dcodex/static/dcodex/images/DCodex-Logo.svg" width="300px">
</p>

![pipline](https://github.com/rbturnbull/dcodex/actions/workflows/pipeline.yml/badge.svg)
[<img src="https://github.com/rbturnbull/dcodex/actions/workflows/docs.yml/badge.svg">](<https://www.dcodex.net>)
[<img src="https://img.shields.io/badge/code%20style-black-000000.svg">](<https://github.com/psf/black>)
[![slack](https://img.shields.io/badge/dcodex-Join%20on%20Slack-green?style=flat&logo=slack)](https://join.slack.com/t/dcodex/shared_invite/zt-y2jpxumc-lDGGr3ZjndVqYLoyfCh1gA)


This is an alpha release of dcodex: a software framework for manuscript analysis.

Some documentation is available at https://www.dcodex.net. More documentation to come. For now, contact me to get a pre-publication version of my PhD thesis where I go into detail regarding the design of the software and each of the components.

# Installation

## General

At the time of writing, dcodex must be run on Python 3.8 or 3.9, so make sure that you have one of these versions downloaded (https://www.python.org/downloads/) and installed on your machine.
You also need to have poetry to build your dcodex project, so make sure that you have it downloaded (https://python-poetry.org/docs/) and installed on your machine.

For a brand new dcodex site, it is easiest to install using [dcodex-cookiecutter](https://github.com/rbturnbull/dcodex-cookiecutter).
Once you have setup your dcodex project using the instructions laid out in that repo, enter the directory for your project.
If your default version of Python is 3.10 or later, you must ensure that poetry is using a virtual environment running version 3.8 or 3.9:

```
poetry env use <path>/<to>/Python38/python

poetry env use <path>/<to>/Python39/python
```

Then install all dependencies for your dcodex project via

```
poetry install
```

## Windows

If you are installing dcodex on Windows, you will need to have Microsoft Visual Studio and C++ Build Tools (https://visualstudio.microsoft.com/vs/) installed on your system.
If you are setting up a dcodex project with dcodex-cookiecutter, make sure you enter `y` for the `windows` option.
If your default version of Python is 3.10 or later, you must ensure that poetry is using a virtual environment running version 3.8 or 3.9:

```
poetry env use <path>\<to>\Python38\python.exe

poetry env use <path>\<to>\Python39\python.exe
```

(If you have the typical installation of Python under your user account, then the first part of this path should be `C:\Users\<you>\AppData\Local\Programs\Python\`.)

## Incorporating into an Existing Django Site

To install dcodex as a plugin in a Django site already set up. Install with pip:
```
pip install dcodex
```

Then add to your installed apps:
```
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
```

Then add the urls to your main urls.py:
```
urlpatterns += [
    path('dcodex/', include('dcodex.urls')),    
]
```

# Other dcodex Packages

The base dcodex app (i.e. this repository) is designed to be used with other apps to give the details for the types of manuscripts being used as well as the textual units. For example, see

* [dcodex_bible](https://github.com/rbturnbull/dcodex_bible)
* [dcodex_lectionary](https://github.com/rbturnbull/dcodex_lectionary)
* [dcodex_chrysostom](https://github.com/rbturnbull/dcodex_chrysostom)
* [dcodex_ashurnasirpal](https://github.com/rbturnbull/dcodex_ashurnasirpal)

There are other dcodex packages to extend the functionality of dcodex such as:

* [dcodex_collation](https://github.com/rbturnbull/dcodex_collation)
* [dcodex_variants](https://github.com/rbturnbull/dcodex_variants)


# Tests and Coverage

To run the tests use the following command:

```
./runtests.py
```

To check the coverage:
```
coverage run -m runtests
coverage report
```

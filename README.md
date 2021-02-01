# dcodex


This is an alpha release of D-Codex: A software framework for manuscript analysis.

Documentation to come. For now, contact me to get a pre-publication version of my PhD thesis where I go into detail regarding the design of the software and each of the components.

# Installation

For a brand new D-Codex site, it is easiest to install using [dcodex-cookiecutter](https://github.com/rbturnbull/dcodex-cookiecutter).

To install dcodex as a plugin in a Django site already set up. Install with pip:
```
pip install -e https://github.com/rbturnbull/dcodex.git#egg=dcodex
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

# Other DCodex packages

The base DCodex app (i.e. this repository) is designed to be used with other apps to give the details for the types of manuscripts being used as well as the textual units. For example, see

* [dcodex_bible](https://github.com/rbturnbull/dcodex_bible)
* [dcodex_lectionary](https://github.com/rbturnbull/dcodex_lectionary)
* [dcodex_chrysostom](https://github.com/rbturnbull/dcodex_chrysostom)
* [dcodex_ashurnasirpal](https://github.com/rbturnbull/dcodex_ashurnasirpal)

There are other DCodex packages to extend the functionality of DCodex such as:

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

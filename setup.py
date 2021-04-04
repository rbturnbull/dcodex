from setuptools import setup

requirements = [
    'Django>3',
    'django-guardian',
    'django-polymorphic',
    'numpy',
    'pandas>=1.0.5',
    'scipy',
    'matplotlib',
    'python-Levenshtein',
    'pyxDamerauLevenshtein', # now an optional install
    'beautifulsoup4',
    'django-admin-sortable2',
    'lxml',
    "regex",
    "django-filer",
    'django-imagedeck @ git+https://gitlab.unimelb.edu.au/rturnbull/django-imagedeck.git#egg=django-imagedeck',
    'gotoh @ git+https://github.com/rbturnbull/gotoh.git#egg=gotoh',
]

setup(
    install_requires=requirements,
)



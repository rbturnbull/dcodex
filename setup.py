from setuptools import setup

requirements = [
    'Django>3',
    'django-polymorphic',
    'numpy',
    'pandas>=1.0.5',
    'scipy',
    'matplotlib',
    'python-Levenshtein',
    'pyxDamerauLevenshtein', # now an optional install
    'beautifulsoup4',
    'django-admin-sortable2',
]

setup(
    install_requires=requirements,
)



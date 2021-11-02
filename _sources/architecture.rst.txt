Architecture
==================================


1.  **Datastore**: The data storage is handled using Django with all the
    database commands happening internally within Django. This means
    that the system can be set up with `several options for the backend
    database system <https://docs.djangoproject.com/en/3.0/ref/databases/>`_. The default setup for Django is to use SQLite which
    has the convenience of storing the database as a single file. Other
    options available are: PostgreSQL, MariaDB, MySQL, and Oracle (with
    other third-party database systems available).

2.  **Models**: The database objects are accessed in code as Django
    'Model' objects. To facilitate extensibility, uses the 'Django
    Polymorphic' package so that the classes in can be subclassed by
    other apps. Users of can interact with the objects in the database
    in Python by using Django's interactive Python shell, or
    through a Python  using the `runscript command <https://django-extensions.readthedocs.io/en/latest/runscript.html>`_, a Jupyter notebook, or through
    `creating a separate Django app <https://docs.djangoproject.com/en/3.1/intro/tutorial01/>`.

3.  **Admin Interface**: A key feature of Django is the ability to
    manipulate the data through the admin interface as an internal
    management tool. Django models can be simply registered to use this
    interface and the display and functionality of of each model can be
    tailored using widgets.

4.  **User Interface**: is designed to be used through a web-browser
    user interface (UI). It can be deployed online (in public or
    private) or be used locally on a user's own computer. The web-pages
    are designed in HTML (using Django's template language) and use
    Javascript through AJAX throughout for a fast, responsive, fluid
    interface. The interface is designed for clarity, simplicity,
    efficiency, and aesthetics. Because the user-interface is HTML based, is
    cross-platform between Windows, Mac, and Linux.


These different tiers allow users to interact with at these different
levels: the web frontend, or through the
Django Admin interface, or directly with Python.

DCodex is designed to be an abstract framework for studying manuscripts. Its
base system is found in the 'app.' This is agnostic as to the type of
manuscript the user can analyse. The particulars of any type of
manuscripts (such as biblical manuscripts or lectionaries) are
implemented in separate apps with sub-classes inheriting from the base
classes in DCodex. 
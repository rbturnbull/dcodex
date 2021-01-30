dcodex-cookiecutter
============================================

To generate a new dcodex project, it is simplest to use the dcodex-cookiecutter project. First, install the `cookiecutter` Python module:

.. code-block:: bash

    pip install cookiecutter

Then, run cookiecutter against the dcodex-cookiecutter repository:

.. code-block:: bash

    cookiecutter https://github.com/rbturnbull/dcodex-cookiecutter

It will ask you a number of questions. Most of the time the defaults are fine. At the end, a Django project using dcodex will be created for you. 
More information about the general project configuration options can be found on the `cookiecutter-django docs <https://cookiecutter-django.readthedocs.io/en/latest/project-generation-options.html>`_.


Answer the prompts with your own desired options. For example:

**Warning**: After this point, change 'Robert Turnbull', 'dcodex_family_13', etc to your own information.

::

    project_name [My DCodex Project]: DCodex Family 13
    project_slug [dcodex_family_13]: dcodex_f13
    description [A brief description my DCodex project.]: A D-Codex project to display the manuscripts of family 13
    author_name [Robert Turnbull]: Robert Turnbull
    domain_name [example.com]: f13.d-codex.net
    email [robert.turnbull@dcodex.net]: rob@robturnbull.com
    version [0.1.0]:
    Select open_source_license:
    1 - Apache Software License 2.0
    2 - MIT
    3 - BSD
    4 - GPLv3
    5 - Not open source
    Choose from 1, 2, 3, 4, 5 [1]:
    timezone [Australia/Melbourne]:
    windows [n]:
    use_pycharm [n]:
    use_docker [y]:
    Select postgresql_version:
    1 - 12.3
    2 - 11.8
    3 - 10.8
    4 - 9.6
    5 - 9.5
    Choose from 1, 2, 3, 4, 5 [1]:
    Select js_task_runner:
    1 - None
    2 - Gulp
    Choose from 1, 2 [1]:
    Select cloud_provider:
    1 - AWS
    2 - GCP
    3 - None
    Choose from 1, 2, 3 [1]:
    Select mail_service:
    1 - Other SMTP
    2 - Mailgun
    3 - Amazon SES
    4 - Mailjet
    5 - Mandrill
    6 - Postmark
    7 - Sendgrid
    8 - SendinBlue
    9 - SparkPost
    Choose from 1, 2, 3, 4, 5, 6, 7, 8, 9 [1]:
    use_async [n]:
    use_drf [y]:
    custom_bootstrap_compilation [n]:
    use_compressor [y]:
    use_celery [y]:
    use_mailhog [n]:
    use_sentry [n]:
    use_whitenoise [y]:
    use_heroku [n]:
    Select ci_tool:
    1 - None
    2 - Travis
    3 - Gitlab
    4 - Github
    Choose from 1, 2, 3, 4 [1]:
    keep_local_envs_in_vcs [y]:
    debug [n]:
    dcodex_url_prefix [dcodex]:
    use_dcodex_bible [n]: y
    use_dcodex_lectionary [n]:
    use_dcodex_collation [n]:
    use_dcodex_variants [n]:
    [SUCCESS]: Project initialized, keep up the good work!

Enter the project and take a look around::

    $ cd dcodex_f13/
    $ ls

Create a PostgreSQL databsae for your project:

::

    $ createdb <what you have entered as the project_slug at setup stage> -U postgres

Now create a Python virtual environment to use with the project:

::

    $ python3 -m venv <virtual env path>
    $ source <virtual env path>/bin/activate

A file called .env is automatically generated. You need to add your PostgreSQL username and password there or otherwise set them us as environment variables.
After that's done, you can source that file.

::

    $ source .env

Now you can install the requirements for the project:

::

    $ pip install -r requirements/local.txt


Now you can fill out the database with the tables required for D-Codex to work:

:: 

    $ ./migrate.sh

You should now be able to run the website on a local server:

::

    $ ./runserver

Create a git repo and push it there::

    $ git init
    $ git add .
    $ git commit -m "Initial commit for dcodex_f13"
    $ git remote add origin git@github.com:rbturnbull/dcodex_f13.git
    $ git push -u origin master



=======================
Introduction: dbservice
=======================

A RESTful web service that stores measurement data from residential homes in the
SmartHG project. It is based on Django and uses the Django REST framework for
providing the Web API for other services.

============
Installation
============


Quickstart for creating a development environment
=================================================

Install Ubuntu packages::

  sudo apt-get install git python-pip postgresql python-virtualenv python-dev libpq-dev

Grant database privileges to current user and create dbservice database::

  sudo -u postgres createuser --superuser $USER
  createdb --encoding=utf-8 dbservice

Get dbservice::

  git clone https://bitbucket.org/smarthg/dbservice
  cd dbservice

Set up development environment using virtualenvwrapper::

    sudo apt-get install virtualenvwrapper
    mkvirtualenv --python=$(which python3.4) dbservice
    workon dbservice
    pip install -r requirements.txt

Alternatively, set up using just virtualenv::

    virtualenv --python=$(which python3.4) dbservice
    source dbservice/bin/activate
    cd path/to/dbservice/repository
    pip install -r requirements.txt


Bootstrap the project
^^^^^^^^^^^^^^^^^^^^^

The project is following the `gitflow` branching strategy. Thus, there are
different stages to enter the development process depending on the purpose of
cloning. The bootstrap process for the **master**-branch is the default
one. However, you will need to ::

  cp dbservice/settings/local.py.example dbservice/settings/local.py
  ./manage.py migrate
  ./manage.py createsuperuser

To bootstrap the **develop**-branch of the project ::

  git checkout -b develop origin/develop
  cp dbservice/settings/local.py.example dbservice/settings/local.py
  ./manage.py migrate
  ./manage.py createsuperuser


Project layout is based on advice from
http://lincolnloop.com/django-best-practices/

Deployment management
=====================

Deployment specific settings are specified in (e.g. packages)::

  fabfile/settings.yaml

Install all the dependencies on target deployment servers from local (i.e. demo, dev or prod)::

  fab -f fabfile/fabfile.py environment:{demo, dev, prod} initialize

*This feature is currently not maintained*

Update the target deployment server from local with newest version from git repository::

  fab -f fabfile/fabfile.py environment:{demo, dev, prod} deploy

*Assumption: Correct initial git configuration and the git repository is read-only.*

Testing
=======

Loading app fixtures to populate database
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In order to test the dbservice, it is convienent to have the database populated
with actual data. In Django this can be done with using fixtures for the particular app::

  ./manage.py loaddata dbservice/apps/homes/fixtures/homes_datadump.json

To dump the the database for an app you do the following::

  ./manage.py dumpdata homes


Building Documentation
======================

Developer documentation is available in ``docs`` and can be built into a number of
formats using `Sphinx <http://pypi.python.org/pypi/Sphinx>`_. To get started::

    pip install Sphinx
    cd docs
    make html

This creates the documentation in HTML format at ``docs/_build/html``.


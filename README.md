capture agent dashboard
================================

all things capture agent

quickstart
----------

clone this project and create a virtualenv:

    git clone https://github.com/nmaekawa/cadash
    cd cadash
    virtualenv venv
    source venv/bin/activate
    pip install -r requirements/dev.txt

then setup the environment variables:

    cd cadash
    vi example.env
    ... set your env vars...
    source example.env

to start a dev server:

    cd cadash
    python manage.py server

you will see a (somewhat) pretty welcome screen.

deployment
----------

this is done via mh-opsworks recipes. see:

- https://github.com/harvard-dce/mh-opsworks
- https://github.com/harvard-dce/mh-opsworks-recipes


running tests
-------------

To run all tests, run :

    cd cadash
    source example.env
    python manage.py test


---eop

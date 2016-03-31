# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
from flask import Flask
from flask import render_template

from cadash import castatus
from cadash import public
from cadash import redunlive
from cadash import user
from cadash import inventory
from cadash.assets import assets
from cadash.extensions import bcrypt
from cadash.extensions import cache
from cadash.extensions import db
from cadash.extensions import debug_toolbar
from cadash.extensions import ldap_cli
from cadash.extensions import login_manager
from cadash.extensions import migrate
from cadash.settings import Config
from cadash.utils import setup_logging

from flask_admin import Admin

def create_app(config_object=None, app_name=__name__):
    """
    An application factory.

    app factory explained here:
    http://flask.pocoo.org/docs/patterns/appfactories/.

    :param config_object: The configuration object to use.
    """
    app = Flask(app_name)
    if config_object is None:
        app.config.from_object(Config())
    else:
        app.config.from_object(config_object)
    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    setup_logging(app)
    return app


def register_extensions(app):
    """Register Flask extensions."""
    assets.init_app(app)
    bcrypt.init_app(app)
    cache.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    debug_toolbar.init_app(app)
    migrate.init_app(app, db)
    ldap_cli.init_app(app)
    return None


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(public.views.blueprint)
    app.register_blueprint(redunlive.views.blueprint)
    app.register_blueprint(castatus.views.blueprint)
    app.register_blueprint(inventory.views.blueprint)
    return None


def register_errorhandlers(app):
    """Register error handlers."""
    def render_error(error):
        """Render error template."""
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, 'code', 500)
        return render_template('{0}.html'.format(error_code)), error_code
    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None

# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
import logging

from flask import Blueprint
from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import login_required

from cadash import __version__ as app_version

blueprint = Blueprint( \
        'castatus', __name__, \
        static_folder='../static', \
        url_prefix='/castatus')


@blueprint.route('/', methods=['GET', 'POST'])
@login_required
def home():
    """castatus home page: all capture agents"""

    # example of logger
    logger = logging.getLogger(current_app.name)
    logger.info('----- this is a log message from app: %s' % current_app.name)

    # Handle logging in
    return render_template('castatus/home.html', version=app_version)


#@blueprint.route('/logout/')
#def logout():
#    """Logout."""
#    logout_user()
#    flash('You are logged out.', 'info')
#    return redirect(url_for('public.home'))

# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
import logging

from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from cadash import __version__ as app_version
from cadash.extensions import cache
from cadash.extensions import login_manager
from cadash.public.forms import LoginForm
from cadash.user.forms import RegisterForm
from cadash.user.models import BaseUser
from cadash.utils import flash_errors

blueprint = Blueprint('public', __name__, static_folder='../static')

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return cache.get(user_id)


@blueprint.route('/', methods=['GET', 'POST'])
def home():
    """Home page."""
    form = LoginForm(request.form)

    # _always_ get logger in request context
    logger = logging.getLogger(__name__)
    logger.info('----- this is a log message from app: %s' % __name__)

    # Handle logging in
    if request.method == 'POST':
        if form.validate_on_submit():
            cache.set(form.user.username, form.user, timeout=24 * 3600)
            login_user(form.user)
            flash('You are logged in.', 'success')
            redirect_url = request.args.get('next') or url_for('public.home')
            return redirect(redirect_url)
        else:
            flash_errors(form)
    return render_template('public/home.html', form=form, version=app_version)


@blueprint.route('/logout/')
@login_required
def logout():
    """Logout."""
    cache.delete(current_user.username)
    logout_user()
    flash('You are logged out.', 'info')
    return redirect(url_for('public.home'))


@blueprint.route('/register/', methods=['GET', 'POST'])
def register():
    """Register new user."""
    form = RegisterForm(request.form, csrf_enabled=False)
    if form.validate_on_submit():
        User.create(username=form.username.data, email=form.email.data, password=form.password.data, active=True)
        flash('Thank you for registering. You can now log in.', 'success')
        return redirect(url_for('public.home'))
    else:
        flash_errors(form)
    return render_template('public/register.html', form=form)


@blueprint.route('/about/')
def about():
    """About page."""
    form = LoginForm(request.form)
    return render_template('public/about.html', form=form, version=app_version)

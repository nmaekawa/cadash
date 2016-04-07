# -*- coding: utf-8 -*-
"""inventory section"""
import json
import logging
import time

from flask import Blueprint
from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required

from cadash import __version__ as app_version
from cadash.inventory.models import Ca
from cadash.inventory.models import Location
from cadash.inventory.models import MhCluster
from cadash.inventory.models import Role
from cadash.inventory.models import Vendor
from cadash.utils import is_authorized

AUTHORIZED_GROUPS = ['deadmin']

blueprint = Blueprint(
        'inventory', __name__,
        static_folder='../static',
        url_prefix='/inventory')


@blueprint.route('/', methods=['GET', 'POST'])
@login_required
def home():
    """inventory home page."""
    if not is_authorized(current_user, AUTHORIZED_GROUPS):
        flash('You need to login, or have no access to inventory pages', 'info')
        return redirect(url_for('public.home', next=request.url))

    # Handle logging in
    return render_template('inventory/home.html', version=app_version)


@blueprint.route('/ca', methods=['GET'])
@login_required
def ca_list():
    """capture agents list."""
    if not is_authorized(current_user, AUTHORIZED_GROUPS):
        flash('You need to login, or have no access to inventory pages', 'info')
        return redirect(url_for('public.home', next=request.url))

    ca_list = Ca.query.order_by(Ca.name).all()
    return render_template('inventory/capture_agent.html',
            version=app_version, ca_list=ca_list)


@blueprint.route('/vendor', methods=['GET'])
@login_required
def vendor_list():
    """vendor list."""
    if not is_authorized(current_user, AUTHORIZED_GROUPS):
        flash('You need to login, or have no access to inventory pages', 'info')
        return redirect(url_for('public.home', next=request.url))

    return render_template('inventory/vendor.html', version=app_version)


@blueprint.route('/cluster', methods=['GET'])
@login_required
def cluster_list():
    """cluster list."""
    if not is_authorized(current_user, AUTHORIZED_GROUPS):
        flash('You need to login, or have no access to inventory pages', 'info')
        return redirect(url_for('public.home', next=request.url))

    return render_template('inventory/cluster.html', version=app_version)


@blueprint.route('/location', methods=['GET'])
@login_required
def location_list():
    """location list."""
    if not is_authorized(current_user, AUTHORIZED_GROUPS):
        flash('You need to login, or have no access to inventory pages', 'info')
        return redirect(url_for('public.home', next=request.url))

    return render_template('inventory/location.html', version=app_version)

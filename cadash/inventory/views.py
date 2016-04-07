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
from cadash.inventory.forms import CaForm
from cadash.inventory.models import Ca
from cadash.inventory.models import Location
from cadash.inventory.models import MhCluster
from cadash.inventory.models import Role
from cadash.inventory.models import Vendor
from cadash.utils import flash_errors
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


@blueprint.route('/ca/list', methods=['GET'])
@login_required
def ca_list():
    """capture agents list."""
    if not is_authorized(current_user, AUTHORIZED_GROUPS):
        flash('You need to login, or have no access to inventory pages', 'info')
        return redirect(url_for('public.home', next=request.url))

    ca_list = Ca.query.order_by(Ca.name).all()
    return render_template('inventory/capture_agent_list.html',
            version=app_version, ca_list=ca_list)


@blueprint.route('/ca', methods=['GET','POST'])
@login_required
def ca_create():
    """capture agents edit."""
    if not is_authorized(current_user, AUTHORIZED_GROUPS):
        flash('You need to login, or have no access to inventory pages', 'info')
        return redirect(url_for('public.home', next=request.url))

    form = CaForm(request.form)
    if form.validate_on_submit():
        try:
            Ca.create(name=form.name.data, address=form.address.data,
                    serial_number=form.serial_number.data,
                    vendor_id=form.vendor_id.data)
        except (InvalidEmptyValueError,
                MissingVendorError,
                DuplicateCaptureAgentNameError,
                DuplicateCaptureAgentAddressError,
                DuplicateCaptureAgentSerialNumberError) as e:
            flash('Error: %s' % e.message, 'error')
        else:
            flash('capture agent created', 'success')
    else:
        flash_errors(form)

    return render_template('inventory/capture_agent_form.html',
            version=app_version, form=form)


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

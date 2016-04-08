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
from cadash.inventory.errors import AssociationError
from cadash.inventory.errors import DuplicateCaptureAgentNameError
from cadash.inventory.errors import DuplicateCaptureAgentAddressError
from cadash.inventory.errors import DuplicateCaptureAgentSerialNumberError
from cadash.inventory.errors import DuplicateLocationNameError
from cadash.inventory.errors import DuplicateMhClusterAdminHostError
from cadash.inventory.errors import DuplicateMhClusterNameError
from cadash.inventory.errors import DuplicateVendorNameModelError
from cadash.inventory.errors import InvalidCaRoleError
from cadash.inventory.errors import InvalidEmptyValueError
from cadash.inventory.errors import InvalidMhClusterEnvironmentError
from cadash.inventory.errors import InvalidOperationError
from cadash.inventory.errors import MissingVendorError
from cadash.inventory.forms import CaForm
from cadash.inventory.forms import LocationForm
from cadash.inventory.forms import MhClusterForm
from cadash.inventory.forms import VendorForm
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


@blueprint.route('/', methods=['GET'])
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
    """capture agent create form."""
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
            flash('capture agent created.', 'success')
    else:
        flash_errors(form)

    return render_template('inventory/capture_agent_form.html',
            version=app_version, form=form, mode='create')


@blueprint.route('/vendor/list', methods=['GET'])
@login_required
def vendor_list():
    """vendor list."""
    if not is_authorized(current_user, AUTHORIZED_GROUPS):
        flash('You need to login, or have no access to inventory pages', 'info')
        return redirect(url_for('public.home', next=request.url))

    v_list = Vendor.query.order_by(Vendor.name_id).all()
    flash('v_list total(%i)' % len(v_list))
    return render_template('inventory/vendor_list.html',
            version=app_version, vendor_list=v_list)


@blueprint.route('/vendor', methods=['GET','POST'])
@login_required
def vendor_create():
    if not is_authorized(current_user, AUTHORIZED_GROUPS):
        flash('You need to login, or have no access to inventory pages', 'info')
        return redirect(url_for('public.home', next=request.url))

    form = VendorForm()
    if form.validate_on_submit():
        try:
            Vendor.create(name=form.name.data, model=form.model.data)
        except (InvalidOperationError,
                DuplicateVendorNameModelError) as e:
            flash('Error: %s' % e.message, 'error')
        else:
            flash('vendor created.', 'success')
    else:
        flash_errors(form)

    return render_template('inventory/vendor_form.html',
            version=app_version, form=form, mode='create')


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

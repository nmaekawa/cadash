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
    return ca_list()

@blueprint.route('/ca/list', methods=['GET'])
@login_required
def ca_list():
    """capture agents list."""
    if not is_authorized(current_user, AUTHORIZED_GROUPS):
        flash('You need to login, or have no access to inventory pages', 'info')
        return redirect(url_for('public.home', next=request.url))

    ca_list = Ca.query.order_by(Ca.name).all()
    return render_template('inventory/capture_agent_list.html',
            version=app_version, record_list=ca_list)


@blueprint.route('/ca', methods=['GET','POST'])
@login_required
def ca_create():
    """capture agent create form."""
    if not is_authorized(current_user, AUTHORIZED_GROUPS):
        flash('You need to login, or have no access to inventory pages', 'info')
        return redirect(url_for('public.home', next=request.url))

    form = CaForm()
    form.vendor_id.choices = get_select_list_for_vendors()
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
            flash('Error: %s' % e.message, 'danger')
        else:
            flash('capture agent created.', 'success')
    else:
        flash_errors(form)

    return render_template('inventory/capture_agent_form.html',
            version=app_version, form=form, mode='create')

def get_select_list_for_vendors():
    """return a list of vendor tuples (id, name_id)."""
    v_list = Vendor.query.order_by(Vendor.name_id).all()
    return [ (v.id, v.name_id) for v in v_list ]


@blueprint.route('/ca/<int:r_id>', methods=['GET','POST'])
@login_required
def ca_edit(r_id):
    """capture agent edit form."""
    if not is_authorized(current_user, AUTHORIZED_GROUPS):
        flash('You need to login, or have no access to inventory pages', 'info')
        return redirect(url_for('public.home', next=request.url))

    ca = Ca.get_by_id(r_id)
    if not ca:
        return render_template('404.html')

    form = CaForm(obj=ca)
    form.vendor_id.choices = get_select_list_for_vendors()
    if form.validate_on_submit():
        try:
            ca.update(name=form.name.data, address=form.address.data,
                    serial_number=form.serial_number.data)
        except (InvalidEmptyValueError,
                MissingVendorError,
                DuplicateCaptureAgentNameError,
                DuplicateCaptureAgentAddressError,
                DuplicateCaptureAgentSerialNumberError) as e:
            flash('Error: %s' % e.message, 'danger')
        else:
            flash('capture agent created.', 'success')
    else:
        flash_errors(form)

    return render_template('inventory/capture_agent_form.html',
            version=app_version, form=form, mode='edit', r_id=ca.id)


@blueprint.route('/vendor/list', methods=['GET'])
@login_required
def vendor_list():
    """vendor list."""
    if not is_authorized(current_user, AUTHORIZED_GROUPS):
        flash('You need to login, or have no access to inventory pages', 'info')
        return redirect(url_for('public.home', next=request.url))

    v_list = Vendor.query.order_by(Vendor.name_id).all()
    return render_template('inventory/vendor_list.html',
            version=app_version, record_list=v_list)


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
            flash('Error: %s' % e.message, 'danger')
        else:
            flash('vendor created.', 'success')
    else:
        flash_errors(form)

    return render_template('inventory/vendor_form.html',
            version=app_version, form=form, mode='create')


@blueprint.route('/vendor/<int:r_id>', methods=['GET','POST'])
@login_required
def vendor_edit(r_id):
    if not is_authorized(current_user, AUTHORIZED_GROUPS):
        flash('You need to login, or have no access to inventory pages', 'info')
        return redirect(url_for('public.home', next=request.url))

    vendor = Vendor.get_by_id(r_id)
    if not vendor:
        return render_template('404.html')

    form = VendorForm(obj=vendor)
    if form.validate_on_submit():
        try:
            vendor.update(name=form.name.data, model=form.model.data)
        except (InvalidOperationError,
                DuplicateVendorNameModelError) as e:
            flash('Error: %s' % e.message, 'danger')
        else:
            flash('vendor updated.', 'success')
    else:
        flash_errors(form)

    return render_template('inventory/vendor_form.html',
            version=app_version, form=form, mode='edit', r_id=vendor.id)


@blueprint.route('/cluster/list', methods=['GET'])
@login_required
def cluster_list():
    """cluster list."""
    if not is_authorized(current_user, AUTHORIZED_GROUPS):
        flash('You need to login, or have no access to inventory pages', 'info')
        return redirect(url_for('public.home', next=request.url))

    c_list = MhCluster.query.order_by(MhCluster.name).all()
    return render_template('inventory/cluster_list.html',
            version=app_version, record_list=c_list)


@blueprint.route('/cluster', methods=['GET','POST'])
@login_required
def cluster_create():
    if not is_authorized(current_user, AUTHORIZED_GROUPS):
        flash('You need to login, or have no access to inventory pages', 'info')
        return redirect(url_for('public.home', next=request.url))

    form = MhClusterForm()
    if form.validate_on_submit():
        try:
            MhCluster.create(name=form.name.data,
                    admin_host=form.admin_host.data,
                    env=form.env.data)
        except (InvalidOperationError,
                InvalidEmptyValueError,
                DuplicateMhClusterAdminHostError,
                DuplicateMhClusterNameError) as e:
            flash('Error: %s' % e.message, 'danger')
        else:
            flash('cluster created.', 'success')
    else:
        flash_errors(form)

    return render_template('inventory/cluster_form.html',
            version=app_version, form=form, mode='create')


@blueprint.route('/cluster/<int:r_id>', methods=['GET','POST'])
@login_required
def cluster_edit(r_id):
    if not is_authorized(current_user, AUTHORIZED_GROUPS):
        flash('You need to login, or have no access to inventory pages', 'info')
        return redirect(url_for('public.home', next=request.url))

    cluster = MhCluster.get_by_id(r_id)
    if not cluster:
        return render_template('404.html')

    form = MhClusterForm(obj=cluster)
    if form.validate_on_submit():
        try:
            cluster.update(name=form.name.data,
                    admin_host=form.admin_host.data,
                    env=form.env.data)
        except (InvalidOperationError,
                InvalidEmptyValueError,
                DuplicateMhClusterAdminHostError,
                DuplicateMhClusterNameError) as e:
            flash('Error: %s' % e.message, 'failure')
        else:
            flash('cluster updated.', 'success')
    else:
        flash_errors(form)

    return render_template('inventory/cluster_form.html',
            version=app_version, form=form, mode='edit', r_id=cluster.id)


@blueprint.route('/location/list', methods=['GET'])
@login_required
def location_list():
    """location list."""
    if not is_authorized(current_user, AUTHORIZED_GROUPS):
        flash('You need to login, or have no access to inventory pages', 'info')
        return redirect(url_for('public.home', next=request.url))

    r_list = Location.query.order_by(Location.name).all()
    return render_template('inventory/location_list.html',
            version=app_version, record_list=r_list)


@blueprint.route('/location', methods=['GET','POST'])
@login_required
def location_create():
    if not is_authorized(current_user, AUTHORIZED_GROUPS):
        flash('You need to login, or have no access to inventory pages', 'info')
        return redirect(url_for('public.home', next=request.url))

    form = LocationForm()
    if form.validate_on_submit():
        try:
            Location.create(name=form.name.data)
        except (InvalidOperationError,
                InvalidEmptyValueError,
                DuplicateLocationNameError) as e:
            flash('Error: %s' % e.message, 'danger')
        else:
            flash('location created.', 'success')
    else:
        flash_errors(form)

    return render_template('inventory/location_form.html',
            version=app_version, form=form, mode='create')


@blueprint.route('/location/<int:r_id>', methods=['GET','POST'])
@login_required
def location_edit(r_id):
    if not is_authorized(current_user, AUTHORIZED_GROUPS):
        flash('You need to login, or have no access to inventory pages', 'info')
        return redirect(url_for('public.home', next=request.url))

    loc = Location.get_by_id(r_id)
    if not loc:
        return render_template('404.html')

    form = LocationForm(obj=loc)
    if form.validate_on_submit():
        try:
            loc.update(name=form.name.data)
        except (InvalidOperationError,
                InvalidEmptyValueError,
                DuplicateLocationNameError) as e:
            flash('Error: %s' % e.message, 'danger')
        else:
            flash('location updated.', 'success')
    else:
        flash_errors(form)

    return render_template('inventory/location_form.html',
            version=app_version, form=form, mode='edit', r_id=loc.id)

############################################################
#
# work in progress -- role admin ui
# http://flask.pocoo.org/snippets/98/
#
@blueprint.route('/role/list', methods=['GET'])
@login_required
def role_list():
    """role list."""
    if not is_authorized(current_user, AUTHORIZED_GROUPS):
        flash('You need to login, or have no access to inventory pages', 'info')
        return redirect(url_for('public.home', next=request.url))

    v_list = Vendor.query.order_by(Vendor.name_id).all()
    return render_template('inventory/vendor_list.html',
            version=app_version, record_list=v_list)


@blueprint.route('/role', methods=['GET','POST'])
@login_required
def role_create():
    if not is_authorized(current_user, AUTHORIZED_GROUPS):
        flash('You need to login, or have no access to inventory pages', 'info')
        return redirect(url_for('public.home', next=request.url))

    form = VendorForm()
    if form.validate_on_submit():
        try:
            Vendor.create(name=form.name.data, model=form.model.data)
        except (InvalidOperationError,
                DuplicateVendorNameModelError) as e:
            flash('Error: %s' % e.message, 'danger')
        else:
            flash('vendor created.', 'success')
    else:
        flash_errors(form)

    return render_template('inventory/vendor_form.html',
            version=app_version, form=form, mode='create')


@blueprint.route('/role/<int:r_id>', methods=['POST'])
@login_required
def role_delete(r_id):
    if not is_authorized(current_user, AUTHORIZED_GROUPS):
        flash('You need to login, or have no access to inventory pages', 'info')
        return redirect(url_for('public.home', next=request.url))

    vendor = Vendor.get_by_id(r_id)
    if not vendor:
        return render_template('404.html')

    form = VendorForm(obj=vendor)
    if form.validate_on_submit():
        try:
            vendor.update(name=form.name.data, model=form.model.data)
        except (InvalidOperationError,
                DuplicateVendorNameModelError) as e:
            flash('Error: %s' % e.message, 'danger')
        else:
            flash('vendor updated.', 'success')
    else:
        flash_errors(form)

    return render_template('inventory/vendor_form.html',
            version=app_version, form=form, mode='edit', r_id=vendor.id)


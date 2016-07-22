# -*- coding: utf-8 -*-
"""inventory section."""

from flask import Blueprint
from flask import flash
from flask import render_template
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
from cadash.inventory.errors import InvalidOperationError
from cadash.inventory.errors import MissingVendorError
from cadash.inventory.forms import CaForm
from cadash.inventory.forms import LocationForm
from cadash.inventory.forms import MhClusterForm
from cadash.inventory.forms import RoleDeleteForm
from cadash.inventory.forms import RoleForm
from cadash.inventory.forms import VendorForm
from cadash.inventory.models import Ca
from cadash.inventory.models import Location
from cadash.inventory.models import MhCluster
from cadash.inventory.models import Role
from cadash.inventory.models import Vendor
from cadash.utils import flash_errors
from cadash.utils import requires_roles

AUTHORIZED_GROUPS = ['deadmin']

blueprint = Blueprint(
        'inventory', __name__,
        static_folder='../static',
        url_prefix='/inventory')


@blueprint.route('/', methods=['GET'])
@login_required
def home():
    """inventory home page."""
    return render_template('inventory/home.html', version=app_version)


@blueprint.route('/ca/list', methods=['GET'])
@login_required
@requires_roles(AUTHORIZED_GROUPS)
def ca_list():
    """capture agents list."""
    ca_list = Ca.query.order_by(Ca.name).all()
    return render_template(
            'inventory/capture_agent_list.html',
            version=app_version, record_list=ca_list)


@blueprint.route('/ca', methods=['GET', 'POST'])
@login_required
@requires_roles(AUTHORIZED_GROUPS)
def ca_create():
    """capture agent create form."""
    form = CaForm()
    form.vendor_id.choices = get_select_list_for_vendors()
    if form.validate_on_submit():
        try:
            Ca.create(
                    name=form.name.data, address=form.address.data,
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

    return render_template(
            'inventory/capture_agent_form.html',
            version=app_version, form=form, mode='create')


def get_select_list_for_vendors():
    """return a list of vendor tuples (id, name_id)."""
    v_list = Vendor.query.order_by(Vendor.name_id).all()
    return [(v.id, v.name_id) for v in v_list]


@blueprint.route('/ca/<int:r_id>', methods=['GET', 'POST'])
@login_required
@requires_roles(AUTHORIZED_GROUPS)
def ca_edit(r_id):
    """capture agent edit form."""
    ca = Ca.get_by_id(r_id)
    if not ca:
        return render_template('404.html')

    form = CaForm(obj=ca)
    form.vendor_id.choices = get_select_list_for_vendors()
    if form.validate_on_submit():
        try:
            ca.update(
                    name=form.name.data, address=form.address.data,
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

    return render_template(
            'inventory/capture_agent_form.html',
            version=app_version, form=form, mode='edit', r_id=ca.id)


@blueprint.route('/vendor/list', methods=['GET'])
@login_required
@requires_roles(AUTHORIZED_GROUPS)
def vendor_list():
    """vendor list."""
    v_list = Vendor.query.order_by(Vendor.name_id).all()
    return render_template(
            'inventory/vendor_list.html',
            version=app_version, record_list=v_list)


@blueprint.route('/vendor', methods=['GET', 'POST'])
@login_required
@requires_roles(AUTHORIZED_GROUPS)
def vendor_create():
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

    return render_template(
            'inventory/vendor_form.html',
            version=app_version, form=form, mode='create')


@blueprint.route('/vendor/<int:r_id>', methods=['GET', 'POST'])
@login_required
@requires_roles(AUTHORIZED_GROUPS)
def vendor_edit(r_id):
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

    return render_template(
            'inventory/vendor_form.html',
            version=app_version, form=form, mode='edit', r_id=vendor.id)


@blueprint.route('/cluster/list', methods=['GET'])
@login_required
@requires_roles(AUTHORIZED_GROUPS)
def cluster_list():
    """cluster list."""
    c_list = MhCluster.query.order_by(MhCluster.name).all()
    return render_template(
            'inventory/cluster_list.html',
            version=app_version, record_list=c_list)


@blueprint.route('/cluster', methods=['GET', 'POST'])
@login_required
@requires_roles(AUTHORIZED_GROUPS)
def cluster_create():
    form = MhClusterForm()
    if form.validate_on_submit():
        try:
            MhCluster.create(
                    name=form.name.data,
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

    return render_template(
            'inventory/cluster_form.html',
            version=app_version, form=form, mode='create')


@blueprint.route('/cluster/<int:r_id>', methods=['GET', 'POST'])
@login_required
@requires_roles(AUTHORIZED_GROUPS)
def cluster_edit(r_id):
    cluster = MhCluster.get_by_id(r_id)
    if not cluster:
        return render_template('404.html')

    form = MhClusterForm(obj=cluster)
    if form.validate_on_submit():
        try:
            cluster.update(
                    name=form.name.data,
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

    return render_template(
            'inventory/cluster_form.html',
            version=app_version, form=form, mode='edit', r_id=cluster.id)


@blueprint.route('/location/list', methods=['GET'])
@login_required
@requires_roles(AUTHORIZED_GROUPS)
def location_list():
    """location list."""
    r_list = Location.query.order_by(Location.name).all()
    return render_template(
            'inventory/location_list.html',
            version=app_version, record_list=r_list)


@blueprint.route('/location', methods=['GET', 'POST'])
@login_required
@requires_roles(AUTHORIZED_GROUPS)
def location_create():
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

    return render_template(
            'inventory/location_form.html',
            version=app_version, form=form, mode='create')


@blueprint.route('/location/<int:r_id>', methods=['GET', 'POST'])
@login_required
@requires_roles(AUTHORIZED_GROUPS)
def location_edit(r_id):
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

    return render_template(
            'inventory/location_form.html',
            version=app_version, form=form, mode='edit', r_id=loc.id)


@blueprint.route('/role/list', methods=['GET'])
@login_required
@requires_roles(AUTHORIZED_GROUPS)
def role_list():
    """role list."""
    form = RoleDeleteForm()
    r_list = Role.query.all()
    return render_template(
            'inventory/role_list.html',
            version=app_version, record_list=r_list, form=form)


@blueprint.route('/role', methods=['GET', 'POST'])
@login_required
@requires_roles(AUTHORIZED_GROUPS)
def role_create():
    form = RoleForm()
    form.ca_id.choices = get_select_list_for_cas()
    form.location_id.choices = get_select_list_for_locations()
    form.cluster_id.choices = get_select_list_for_clusters()
    if form.validate_on_submit():
        ca = Ca.get_by_id(form.ca_id.data)
        loc = Location.get_by_id(form.location_id.data)
        cluster = MhCluster.get_by_id(form.cluster_id.data)
        try:
            Role.create(
                    name=form.role_name.data,
                    ca=ca, location=loc, cluster=cluster)
        except (InvalidCaRoleError,
                AssociationError) as e:
            flash('Error: %s' % e.message, 'danger')
        else:
            flash('role created.', 'success')
    else:
        flash_errors(form)

    return render_template(
            'inventory/role_form.html',
            version=app_version, form=form, mode='create')


def get_select_list_for_cas():
    """return a list of ca tuples (id, name_id)."""
    ca_list = Ca.query.filter(Ca.role is None).all()
    return [(c.id, c.name_id) for c in ca_list]


def get_select_list_for_locations():
    """return a list of location tuples (id, name_id)."""
    r_list = Location.query.order_by(Location.name).all()
    return [(r.id, r.name_id) for r in r_list]


def get_select_list_for_clusters():
    """return a list of cluster tuples (id, name_id)."""
    r_list = MhCluster.query.order_by(MhCluster.name).all()
    return [(r.id, r.name_id) for r in r_list]


@blueprint.route('/role/delete/<int:r_id>', methods=['POST'])
@login_required
@requires_roles(AUTHORIZED_GROUPS)
def role_delete(r_id):
    form = RoleDeleteForm()
    role = Role.query.filter_by(ca_id=r_id).first()
    if not role:
        return render_template('404.html')

    if form.validate_on_submit():
        try:
            role.delete()
        except (InvalidCaRoleError,
                AssociationError) as e:
            flash('Error: %s' % e.message, 'danger')
        else:
            flash('role deleted.', 'success')
    else:
        flash_errors(form)

    r_list = Role.query.all()
    return render_template(
            'inventory/role_list.html',
            version=app_version, form=form, record_list=r_list)

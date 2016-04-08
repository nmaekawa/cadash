# -*- coding: utf-8 -*-
"""inventory forms."""
from flask_wtf import Form
from wtforms import SelectField
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.validators import URL

from cadash.inventory.models import Ca
from cadash.inventory.models import CA_ROLES
from cadash.inventory.models import Location
from cadash.inventory.models import MhCluster
from cadash.inventory.models import MH_ENVS
from cadash.inventory.models import Vendor
from cadash import utils


class CaForm(Form):
    """form for capture agent."""

    vendor_id = SelectField('vendor', coerce=int, validators=[DataRequired()])
    name = StringField('name', validators=[DataRequired()])
    address = StringField('address',
            validators=[DataRequired(), URL(require_tld=False)])
    serial_number = StringField('serial_number')


class MhClusterForm(Form):
    """form for mh cluster."""

    name = StringField('name', validators=[DataRequired()])
    admin_host = StringField('admin_host',
            validators=[DataRequired(), URL(require_tld=False)])
    env = SelectField('environment',
            choices=[(e, e) for e in MH_ENVS],
            validators=[DataRequired()])


class VendorForm(Form):
    """form for vendor."""

    name = StringField('name', validators=[DataRequired()])
    model = StringField('model', validators=[DataRequired()])


class LocationForm(Form):
    """form for location."""

    name = StringField('name', validators=[DataRequired()])


class RoleForm(Form):
    """form for role."""

    name = SelectField('role',
            choices=[(r, r) for r in CA_ROLES],
            validators=[DataRequired()])
    ca_id = SelectField('capture_agent', coerce=int,
            validators=[DataRequired()])
    location_id = SelectedField['location', coerce=int,
            validators=[DataRequired()])
    cluster_id = SelectedField['cluster', coerce=int,
            validators=[DataRequired()])

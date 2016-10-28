# -*- coding: utf-8 -*-
"""inventory forms."""
from flask_wtf import Form
import pytz
from wtforms import BooleanField
from wtforms import IntegerField
from wtforms import PasswordField
from wtforms import SelectField
from wtforms import StringField
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms.validators import URL

from cadash.inventory.models import CA_ROLES
from cadash.inventory.models import CA_STATES
from cadash.inventory.models import MH_ENVS


class CaForm(Form):
    """form for capture agent."""

    vendor_id = SelectField('vendor', coerce=int, validators=[DataRequired()])
    name = StringField('name', validators=[DataRequired()])
    address = StringField(
            'address', validators=[DataRequired(), URL(require_tld=False)])
    serial_number = StringField('serial_number')
    capture_card_id = StringField('capture_card_id')
    state = SelectField(
            'state',
            choices=[(s, s.upper()) for s in CA_STATES],
            validators=[DataRequired()])


class MhClusterForm(Form):
    """form for mh cluster."""

    name = StringField('name', validators=[DataRequired()])
    admin_host = StringField(
            'admin_host', validators=[DataRequired(), URL(require_tld=False)])
    env = SelectField(
            'environment',
            choices=[(e, e) for e in MH_ENVS],
            validators=[DataRequired()])


class VendorForm(Form):
    """form for vendor."""

    __tz_choices__ = [(x, x) for x in pytz.all_timezones]

    name = StringField('name', validators=[DataRequired()])
    model = StringField('model', validators=[DataRequired()])
    touchscreen_timeout_secs = IntegerField(
            'touchscreen_timout_secs', validators=[DataRequired()])
    touchscreen_allow_recording = BooleanField('touchscreen_allow_recording')
    maintenance_permanent_logs = BooleanField('maintenance_permanent_logs')
    datetime_timezone = SelectField(
            'datetime_timezone', choices=__tz_choices__,
            validators=[DataRequired()])
    datetime_ntpserver = StringField(
            'datetime_ntpserver', validators=[DataRequired()])
    firmware_version = StringField(
            'firmware_version', validators=[DataRequired()])
    source_deinterlacing = BooleanField('source_deinterlacing')
    # beware of BooleanFields: the html form will not send a
    # boolean_var_name=False, it will just omit the var when it's set to False.
    # if you add a validator=[DataRequired()] to a BooleanField, it fails when
    # you want to set the var to False! it's what happens in my unit tests...


class LocationForm(Form):
    """form for location."""

    __vconnector_choices__ = [('hdmi', 'HDMI'), ('sdi', 'SDI'), ('vga', 'VGA')]
    __vinput_choices__ = [('a', 'A'), ('b', 'B')]

    name = StringField('name', validators=[DataRequired()])
    primary_pr_vconnector = SelectField(
            'primary_pr_vconnector',
            choices=__vconnector_choices__, validators=[DataRequired()])
    primary_pn_vconnector = SelectField(
            'primary_pn_vconnector',
            choices=__vconnector_choices__, validators=[DataRequired()])
    secondary_pr_vconnector = SelectField(
            'secondary_pr_vconnector',
            choices=__vconnector_choices__, validators=[DataRequired()])
    secondary_pn_vconnector = SelectField(
            'secondary_pn_vconnector',
            choices=__vconnector_choices__, validators=[DataRequired()])
    primary_pr_vinput = SelectField(
            'primary_pr_vinput',
            choices=__vinput_choices__, validators=[DataRequired()])
    primary_pn_vinput = SelectField(
            'primary_pn_vinput',
            choices=__vinput_choices__, validators=[DataRequired()])
    secondary_pr_vinput = SelectField(
            'primary_pr_vinput',
            choices=__vinput_choices__, validators=[DataRequired()])
    secondary_pn_vinput = SelectField(
            'primary_pn_vinput',
            choices=__vinput_choices__, validators=[DataRequired()])


class RoleForm(Form):
    """form for role."""

    role_name = SelectField(
            'role',
            choices=[(r, r) for r in CA_ROLES],
            validators=[DataRequired()])
    ca_id = SelectField(
            'capture_agent', coerce=int, validators=[DataRequired()])
    location_id = SelectField(
            'location', coerce=int, validators=[DataRequired()])
    cluster_id = SelectField(
            'cluster', coerce=int, validators=[DataRequired()])


class RoleDeleteForm(Form):
    """form for deleting role."""

    r_id = IntegerField('r_id', validators=[DataRequired()])


class AkamaiStreamingConfigForm(Form):
    """form for streaming configs."""

    name = StringField('name', validators=[DataRequired()])
    comment = TextAreaField('comment')
    stream_id = StringField('stream_id', validators=[DataRequired()])
    stream_user = StringField('stream_user', validators=[DataRequired()])
    stream_password = PasswordField(
            'stream_password', validators=[DataRequired()])
    #primary_url_jinja2_template = StringField(
    #        'primary_url_jinja2_template', validators=[DataRequired()])
    #secondary_url_jinja2_template = StringField(
    #        'secondary_url_jinja2_template', validators=[DataRequired()])
    #stream_name_jinja2_template = StringField(
    #        'stream_name_jinja2_template', validators=[DataRequired()])

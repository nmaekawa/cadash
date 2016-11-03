# -*- coding: utf-8 -*-
"""inventory forms."""
from flask_wtf import FlaskForm
import pytz
from wtforms import BooleanField
from wtforms import IntegerField
from wtforms import HiddenField
from wtforms import PasswordField
from wtforms import SelectField
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.validators import URL

from cadash.inventory.models import CA_ROLES
from cadash.inventory.models import CA_STATES
from cadash.inventory.models import MH_ENVS


class CaForm(FlaskForm):
    """form for capture agent."""

    vendor_id = SelectField('vendor', coerce=int, validators=[DataRequired()])
    name = StringField('name', validators=[DataRequired()])
    address = StringField(
            'address', validators=[URL(require_tld=False)])
    serial_number = StringField('serial_number')
    capture_card_id = StringField('capture_card_id')
    state = SelectField(
            'state',
            choices=[(s, s.upper()) for s in CA_STATES],
            validators=[DataRequired()], default=u'setup')


class MhClusterForm(FlaskForm):
    """form for mh cluster."""

    name = StringField('name', validators=[DataRequired()])
    admin_host = StringField(
            'admin_host', validators=[DataRequired(), URL(require_tld=False)])
    env = SelectField(
            'environment',
            choices=[(e, e) for e in MH_ENVS],
            validators=[DataRequired()])
    username = StringField('name')
    password = PasswordField('password')


class VendorForm(FlaskForm):
    """form for vendor."""

    __tz_choices__ = [(x, x) for x in pytz.all_timezones]

    name = StringField('name', validators=[DataRequired()])
    model = StringField('model', validators=[DataRequired()])
    touchscreen_timeout_secs = IntegerField('touchscreen_timout_secs')
    touchscreen_allow_recording = BooleanField('touchscreen_allow_recording')
    maintenance_permanent_logs = BooleanField('maintenance_permanent_logs')
    datetime_timezone = SelectField(
            'datetime_timezone', choices=__tz_choices__,
            default='US/Eastern')
    datetime_ntpserver = StringField('datetime_ntpserver')
    firmware_version = StringField('firmware_version')
    source_deinterlacing = BooleanField('source_deinterlacing')
    # beware of BooleanFields: the html form will not send a
    # boolean_var_name=False, it will just omit the var when it's set to False.
    # if you add a validator=[DataRequired()] to a BooleanField, it fails when
    # you want to set the var to False! it's what happens in my unit tests...


class NameRequiredForm(FlaskForm):
    """form with string field `name` required."""
    name = StringField('name', validators=[DataRequired()])


class LocationUpdateForm(FlaskForm):
    """form for location."""

    __connector_input_choices__ = [
            ('hdmi-a', 'HDMI-A'), ('hdmi-b', 'HDMI-B'),
            ('sdi-a', 'SDI-A'), ('sdi-b', 'SDI-B'),
            ('vga-a', 'VGA-A'), ('vga-b', 'VGA-B')]

    name = StringField('name')
    primary_pr = SelectField(
            'primary_pr', choices=__connector_input_choices__,
            validators=[DataRequired()])
    primary_pn = SelectField(
            'primary_pn', choices=__connector_input_choices__,
            validators=[DataRequired()])
    secondary_pr = SelectField(
            'secondary_pr', choices=__connector_input_choices__,
            validators=[DataRequired()])
    secondary_pn = SelectField(
            'secondary_pn', choices=__connector_input_choices__,
            validators=[DataRequired()])


class RoleForm(FlaskForm):
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


class RoleDeleteForm(FlaskForm):
    """form for deleting role."""

    r_id = IntegerField('r_id', validators=[DataRequired()])


class AkamaiStreamingConfigForm(FlaskForm):
    """form for streaming configs."""

    name = StringField('name', validators=[DataRequired()])
    comment = StringField('comment')
    stream_id = StringField('stream_id', validators=[DataRequired()])
    stream_user = StringField('stream_user', validators=[DataRequired()])
    stream_password = PasswordField('stream_password')
    primary_url_jinja2_template = StringField('primary_url_jinja2_template')
    secondary_url_jinja2_template = StringField('secondary_url_jinja2_template')
    stream_name_jinja2_template = StringField('stream_name_jinja2_template')


class MhpearlConfigForm(FlaskForm):
    """form for mhpearl non-deduceable configs."""

    comment = StringField('comment')
    mhpearl_version = StringField('mhpearl_version')
    file_search_range_in_sec = IntegerField(
            'file_search_range_in_sec', validators=[DataRequired()])
    update_frequency_in_sec = IntegerField(
            'update_frequency_in_sec', validators=[DataRequired()])


class EpiphanChannelForm(FlaskForm):
    """form for epiphan channel config."""

    name = HiddenField('name', validators=[DataRequired()])
    channel_id_in_device = IntegerField(
            'channel_id_in_device', validators=[DataRequired()])
    stream_cfg_id = SelectField(
            'stream_cfg_id', coerce=int, validators=[DataRequired()])

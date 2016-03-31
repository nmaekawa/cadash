# -*- coding: utf-8 -*-
"""inventory forms."""
from flask_wtf import Form
from wtforms import SelectField
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.validators import URL

from cadash.inventory.models import Ca
from cadash.inventory.models import Location
from cadash.inventory.models import MhCluster
from cadash.inventory.models import MH_ENVS
from cadash.inventory.models import Vendor
from cadash import utils


class CaForm(Form):
    """form for capture agent."""

    vendor_id = SelectField('vendor', coerce=int, validators=[DataRequired()])
    name = StringField('name', validators=[DataRequired()])
    address = StringField('address', validators=[DataRequired(),URL()])
    serial_number = StringField('serial_number')

    def validate(self):
        """Validate the form."""
        initial_validation = super(CaForm, self).validate()
        if not initial_validation:
            return False

        ca = Ca.query.filter_by(serial_number=self.serial_number.data).first()
        if ca:
            self.serial_number.errors.append(
                    'ca with same serial number already in inventory')
            return False

        ca = Ca.query.filter_by(address=self.address.data).first()
        if ca:
            self.address.errors.append(
                    'ca with same address already in inventory')
            return False

        ca = Ca.query.filter_by(name=self.name.data).first()
        if ca:
            self.name.errors.append(
                    'ca with same name already in inventory')
            return False

        return True


class MhClusterForm(Form):
    """form for mh cluster."""

    name = StringField('name', validators=[DataRequired()])
    admin_host = StringField('admin_host', validators=[DataRequired(), URL()])
    env = SelectField('environment',
            choices=[(e, e) for e in MH_ENVS],
            validators=[DataRequired()])

    def validate(self):
        """Validate the form."""
        initial_validation = super(MhClusterForm, self).validate()
        if not initial_validation:
            return False

        cluster = MhCluster.query.filter_by(
                admin_host=self.admin_host.data).first()
        if cluster:
            self.admin_host.errors.append(
                    'cluster with same admin host address already in inventory')
            return False

        cluster = MhCluster.query.filter_by(name=self.name.data).first()
        if cluster:
            self.name.errors.append(
                    'cluster with same name already in inventory')
            return False

        return True


class VendorForm(Form):
    """form for vendor."""

    name = StringField('name', validators=[DataRequired()])
    model = StringField('model', validators=[DataRequired()])

    def validate(self):
        """Validate the form."""
        initial_validation = super(VendorForm, self).validate()
        if not initial_validation:
            return False

        vendor_name_id = "%s_%s" % (utils.clean_name(self.name.data),
                utils.clean_name(self.model.data))
        vendor = Vendor.query.filter_by(name_id=vendor_name_id).first()
        if vendor:
            self.name.errors.append(
                    'vendor-model already in inventory')
            return False

        return True


class LocationForm(Form):
    """form for location."""

    name = StringField('name', validators=[DataRequired()])

    def validate(self):
        """Validate the form."""
        initial_validation = super(LocationForm, self).validate()
        if not initial_validation:
            return False

        room = Location.query.filter_by(name=self.name.data).first()
        if room:
            self.name.errors.append(
                    'location already in inventory')
            return False

        return True

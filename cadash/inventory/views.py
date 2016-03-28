# -*- coding: utf-8 -*-
"""views for inventory."""

from flask import abort
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
import logging

from cadash.database import db
from cadash.inventory.models import Ca
from cadash.inventory.models import Location
from cadash.inventory.models import Vendor
from cadash.inventory.models import MhCluster
from cadash.inventory.models import Role

class CadashInventoryModelView(ModelView):
    """base model view for inventory."""

    def is_accessible(self):
        """only admins can access model views."""
        if current_user.is_authenticated and current_user.is_in_group('deadmin'):
            return True
        return False

    def inacessible_callback(self, name, **kwargs):
        """redirect to login page if no access."""
        #flash('You need to login, or have no access to admin pages', 'info')
        #return redirect(url_for('public.home'))
        return redirect(url_for('login', next=request.url))

    def _handle_view(self, name, **kwargs):
        """override builtin _handle_view to redirect users to cadash.home."""
        if not self.is_accessible():
            if current_user.is_authenticated:
                about(403)
            else:
                return redirect(url_for('public.home', next=request.url))


class CaptureAgentModelView(CadashInventoryModelView):
    """view for capture agent model."""
    can_delete = False


class LocationModelView(CadashInventoryModelView):
    """view for location model."""
    can_delete = False


class VendorModelView(CadashInventoryModelView):
    """view for vendor model."""
    can_delete = False


class MhClusterModelView(CadashInventoryModelView):
    """view for mh cluster model view."""
    can_delete = False


class RoleModelView(CadashInventoryModelView):
    """view for capture agent role in room."""
    can_delete = True


def init_inventory_views(admin):
    admin.add_view(CaptureAgentModelView(Ca, db.session))
    admin.add_view(LocationModelView(Location, db.session))
    admin.add_view(VendorModelView(Vendor, db.session))
    admin.add_view(MhClusterModelView(MhCluster, db.session))
    admin.add_view(RoleModelView(Role, db.session))

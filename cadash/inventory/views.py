# -*- coding: utf-8 -*-
"""views for inventory."""

from flask_admin.contrib.sqla import ModelView

from cadash.database import db
from cadash.inventory.models import Ca
from cadash.inventory.models import Location
from cadash.inventory.models import Vendor
from cadash.inventory.models import MhCluster

class CaptureAgentModelView(ModelView):
    """view for capture agent model."""
    create_modal = True


class LocationModelView(ModelView):
    """view for location model."""
    can_delete = False


class VendorModelView(ModelView):
    """view for vendor model."""
    can_delete = False


class MhClusterModelView(ModelView):
    """view for mh cluster model view."""
    create_modal = True


def init_inventory_views(admin):
    admin.add_view(CaptureAgentModelView(Ca, db.session))
    admin.add_view(LocationModelView(Location, db.session))
    admin.add_view(VendorModelView(Vendor, db.session))
    admin.add_view(MhClusterModelView(MhCluster, db.session))

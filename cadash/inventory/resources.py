# -*- coding: utf-8 -*-
"""rest resources inventory section"""
import json
import logging
import time

from flask import current_app
from flask import request
from flask_login import current_user
from flask_login import login_required
from flask_restful import Api
from flask_restful import Resource
from flask_restful import abort
from flask_restful import fields
from flask_restful import marshal
from flask_restful import marshal_with
from flask_restful import reqparse

from cadash import __version__ as app_version
from cadash.inventory.models import Ca
from cadash.inventory.models import Location
from cadash.inventory.models import MhCluster
from cadash.inventory.models import Role
from cadash.inventory.models import Vendor


def register_resources(api):
    """add resources to rest-api."""
    api.add_resource(CaAPI, '/inventory/api/cas/<int:ca_id>', endpoint='api_ca')
    api.add_resource(CaListAPI, '/inventory/api/cas', endpoint='api_calist')


def abort_if_none(resource, resource_id):
    """ return 404."""
    if resource is None:
        abort(404, message='resource not found (%s)' % resource_id)

# dicts to define output json objects
# for flask_restful.marshal_with
vendor_fields = {
        'id': fields.Integer,
        'name': fields.String,
        'model': fields.String,
        'name_id': fields.String
        }
ca_fields = {
        'id': fields.Integer,
        'name': fields.String,
        'address': fields.String,
        'serial_number': fields.String(default='not available'),
        'vendor_name_id': fields.String(attribute='vendor.name_id')
        }
location_fields = {
        'id': fields.Integer,
        'name': fields.String
        }
cluster_fields = {
        'id': fields.Integer,
        'name': fields.String,
        'admin_host': fields.String,
        'env': fields.String
        }


class CaAPI(Resource):
    """capture agent resource."""

    @marshal_with(ca_fields)
    def get(self, ca_id):
        ca = Ca.get_by_id(ca_id)
        abort_if_none(ca, 'capture_agent[%s]' % ca_id)
        return ca


    def put(self, ca_id):
        ca = Ca.get_by_id(ca_id)
        abort_if_none(ca, 'capture_agent[%s]' % ca_id)

        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, location='json')
        parser.add_argument('address', type=str, location='json')
        parser.add_argument('serial_number', type=str, location='json')
        args = parser.parse_args()

        # FIXME: catch errors to return some usr-friendly msg
        ca.update(name=args['name'], address=args['address'],
                serial_number=args['serial_number'])
        return marshal(ca, Ca), 201


    def delete(self, ca_id):
        ca = Ca.get_by_id(ca_id)
        if not ca is None:
            ca.delete()
        return '', 204


class CaListAPI(Resource):
    """capture agent list resource."""

    @marshal_with(ca_fields)
    def get(self):
        ca_list = Ca.query.order_by(Ca.name).all()
        logger = logging.getLogger(__name__)
        logger.debug('ca_list is %s' % ca_list)
        return ca_list


    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True,
            help='`name` cannot be blank', location='json')
        parser.add_argument('address', type=str, required=True,
            help='`address` cannot be blank', location='json')
        parser.add_argument('serial_number', type=str, location='json')
        parser.add_argument('vendor_id', type=int, location='json')
        args = parser.parse_args()

        # 404 if vendor not in inventory
        vendor = Vendor.get_by_id(args['vendor_id'])
        abort_if_none(vendor, args['vendor_id'])

        # FIXME: catch errors to return some usr-friendly msg
        ca = Ca.create(name=args['name'],
                address=args['address'],
                serial_number=args['serial_number'],
                vendor=vendor)
        return marshal(ca, ca_fields), 201

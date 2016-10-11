# -*- coding: utf-8 -*-
"""rest resources inventory section."""

from flask_login import login_required
from flask_restful import Resource
from flask_restful import abort
from flask_restful import fields
from flask_restful import marshal
from flask_restful import reqparse

from cadash.inventory.errors import AssociationError
from cadash.inventory.errors import DuplicateCaptureAgentNameError
from cadash.inventory.errors import DuplicateCaptureAgentAddressError
from cadash.inventory.errors import DuplicateCaptureAgentSerialNumberError
from cadash.inventory.errors import DuplicateEpiphanChannelError
from cadash.inventory.errors import DuplicateEpiphanChannelIdError
from cadash.inventory.errors import DuplicateEpiphanRecorderError
from cadash.inventory.errors import DuplicateEpiphanRecorderIdError
from cadash.inventory.errors import DuplicateLocationNameError
from cadash.inventory.errors import DuplicateMhClusterAdminHostError
from cadash.inventory.errors import DuplicateMhClusterNameError
from cadash.inventory.errors import DuplicateVendorNameModelError
from cadash.inventory.errors import InvalidCaRoleError
from cadash.inventory.errors import InvalidEmptyValueError
from cadash.inventory.errors import InvalidJsonValueError
from cadash.inventory.errors import InvalidMhClusterEnvironmentError
from cadash.inventory.errors import InvalidOperationError
from cadash.inventory.errors import InvalidTimezoneError
from cadash.inventory.errors import MissingVendorError
from cadash.inventory.models import Ca
from cadash.inventory.models import Location
from cadash.inventory.models import MhCluster
from cadash.inventory.models import Role
from cadash.inventory.models import Vendor


# dicts to define output json objects
# for flask_restful.marshal_with
RESOURCE_FIELDS = {
        'Vendor': {
            'id': fields.Integer,
            'name_id': fields.String,
            'name': fields.String,
            'model': fields.String,
            'config_id': fields.Integer,
            'datetime_ntpserver': fields.String(attribute='config.datetime_ntpserver'),
            'datetime_timezone': fields.String(attribute='config.datetime_timezone'),
            'firmware_version': fields.String(attribute='config.firmware_version'),
            'maintenance_permanent_logs': fields.Boolean(attribute='config.maintenance_permanent_logs'),
            'source_deinterlacing': fields.Boolean(attribute='source_deinterlacing'),
            'touchscreen_allow_recording': fields.Boolean(attribute='touchscreen_allow_recording'),
            'touchscreen_timeout_secs': fields.Integer(attribute='touchscreen_timeout_secs'),
        },
        'Ca': {
            'id': fields.Integer,
            'name': fields.String,
            'name_id': fields.String,
            'address': fields.String,
            'serial_number': fields.String(default='not available'),
            'vendor_name_id': fields.String(attribute='vendor.name_id'),
            'capture_card_id': fields.String(default='not available'),
        },
        'Location': {
            'id': fields.Integer,
            'name_id': fields.String,
            'name': fields.String,
            'config_id': fields.Integer,
        },
        'MhCluster': {
            'id': fields.Integer,
            'name_id': fields.String,
            'name': fields.String,
            'admin_host': fields.String,
            'env': fields.String,
        },
        'Role': {
            'name': fields.String,
            'ca_id': fields.Integer,
            'location_id': fields.Integer,
            'cluster_id': fields.Integer,
            'config_id': fields.Integer,
        },
}


def register_resources(api):
    """add resources to rest-api."""
    api.add_resource(
            Ca_API,
            '/api/inventory/cas/<int:r_id>', endpoint='api_ca')
    api.add_resource(
            Ca_ListAPI,
            '/api/inventory/cas', endpoint='api_calist')
    api.add_resource(
            Location_API,
            '/api/inventory/locations/<int:r_id>', endpoint='api_location')
    api.add_resource(
            Location_ListAPI,
            '/api/inventory/locations', endpoint='api_locationlist')
    api.add_resource(
            Vendor_API,
            '/api/inventory/vendors/<int:r_id>', endpoint='api_vendor')
    api.add_resource(
            Vendor_ListAPI,
            '/api/inventory/vendors', endpoint='api_vendorlist')
    api.add_resource(
            MhCluster_API,
            '/api/inventory/clusters/<int:r_id>', endpoint='api_cluster')
    api.add_resource(
            MhCluster_ListAPI,
            '/api/inventory/clusters', endpoint='api_clusterlist')
    api.add_resource(
            Role_API,
            '/api/inventory/roles/<int:r_id>', endpoint='api_role')
    api.add_resource(
            Role_ListAPI,
            '/api/inventory/roles', endpoint='api_rolelist')


def abort_404_if_resource_none(resource, resource_id):
    """return 404."""
    if resource is None:
        abort(404, message='resource not found (%s)' % resource_id)


class Resource_API(Resource):
    """base resource for rest api: get, put, delete."""

    def __init__(self):
        """create instance."""
        super(Resource_API, self).__init__()

        # name of the model class this resource is based on
        self._resource_model_class_name = type(self).__name__.split('_')[0]
        # actual model class object this resource is based on
        self._resource_model_class = globals()[self._resource_model_class_name]
        # arg parser for updates - must be init'd by child class
        self._parser_update = reqparse.RequestParser()
        # decorators for authenticated rest-endpoints
        self.method_decorators = [login_required]


    def get(self, r_id):
        resource = self._resource_model_class.get_by_id(r_id)
        abort_404_if_resource_none(
                resource,
                '%s[%i]' % (self._resource_model_class_name, r_id))
        return marshal(
                resource,
                RESOURCE_FIELDS[self._resource_model_class_name]), 200


    def put(self, r_id):
        resource = self._resource_model_class.get_by_id(r_id)
        abort_404_if_resource_none(
                resource,
                '%s[%i]' % (self._resource_model_class_name, r_id))

        args = self._parser_update.parse_args()
        try:
            resource.update(**args)
        except (AssociationError,
                DuplicateCaptureAgentNameError,
                DuplicateCaptureAgentAddressError,
                DuplicateCaptureAgentSerialNumberError,
                DuplicateEpiphanChannelError,
                DuplicateEpiphanChannelIdError,
                DuplicateEpiphanRecorderError,
                DuplicateEpiphanRecorderIdError,
                DuplicateLocationNameError,
                DuplicateMhClusterAdminHostError,
                DuplicateMhClusterNameError,
                DuplicateVendorNameModelError,
                InvalidCaRoleError,
                InvalidEmptyValueError,
                InvalidJsonValueError,
                InvalidMhClusterEnvironmentError,
                InvalidOperationError,
                InvalidTimezoneError,
                MissingVendorError) as e:
            abort(400, message=e.message)
        else:
            return marshal(
                    resource,
                    RESOURCE_FIELDS[self._resource_model_class_name]), 200

    def delete(self, r_id):
        resource = self._resource_model_class.get_by_id(r_id)
        if not resource:
            resource.delete()
        return '', 204


class Resource_ListAPI(Resource):
    """base resource for rest api: get list, post."""

    def __init__(self):
        """create instance."""
        super(Resource_ListAPI, self).__init__()

        # name of the model class this resource is based on
        self._resource_model_class_name = type(self).__name__.split('_')[0]
        # actual model class object this resource is based on
        self._resource_model_class = globals()[self._resource_model_class_name]
        # arg parser for creates - must be init'd by child class
        self._parser_create = reqparse.RequestParser()
        # decorators for authenticated rest-endpoints
        self.method_decorators = [login_required]


    def get(self):
        resource_list = self._resource_model_class.query.all()
        return marshal(
                resource_list,
                RESOURCE_FIELDS[self._resource_model_class_name]), 200

    def post(self):
        args = self._parser_create.parse_args()
        try:
            resource = self._resource_model_class.create(**args)
        except (AssociationError,
                DuplicateCaptureAgentNameError,
                DuplicateCaptureAgentAddressError,
                DuplicateCaptureAgentSerialNumberError,
                DuplicateEpiphanChannelError,
                DuplicateEpiphanChannelIdError,
                DuplicateEpiphanRecorderError,
                DuplicateEpiphanRecorderIdError,
                DuplicateLocationNameError,
                DuplicateMhClusterAdminHostError,
                DuplicateMhClusterNameError,
                DuplicateVendorNameModelError,
                InvalidCaRoleError,
                InvalidEmptyValueError,
                InvalidJsonValueError,
                InvalidMhClusterEnvironmentError,
                InvalidOperationError,
                InvalidTimezoneError,
                MissingVendorError) as e:
            abort(400, message=e.message)
        else:
            return marshal(
                    resource,
                    RESOURCE_FIELDS[self._resource_model_class_name]), 201


class Ca_API(Resource_API):
    """capture agent resource."""

    def __init__(self):
        """create instance."""
        super(Ca_API, self).__init__()
        self._parser_update.add_argument(
                'name', type=str,
                location='json', store_missing=False)
        self._parser_update.add_argument(
                'address', type=str,
                location='json', store_missing=False)
        self._parser_update.add_argument(
                'serial_number', type=str,
                location='json', store_missing=False)


class Ca_ListAPI(Resource_ListAPI):
    """capture agent list and create resource."""

    def __init__(self):
        """create instance."""
        super(Ca_ListAPI, self).__init__()
        self._parser_create.add_argument(
                'name', type=str, required=True,
                help='`name` cannot be blank', location='json')
        self._parser_create.add_argument(
                'address', type=str, required=True,
                help='`address` cannot be blank', location='json')
        self._parser_create.add_argument(
                'vendor_id', type=int, required=True,
                help='`vendor` cannet be blank', location='json')
        self._parser_create.add_argument(
                'serial_number', type=str,
                location='json', store_missing=False)


class Location_API(Resource_API):
    """location resource for rest endpoints."""

    def __init__(self):
        """create instance."""
        super(Location_API, self).__init__()
        self._parser_update.add_argument(
                'name', type=str, location='json',
                store_missing=False)


class Location_ListAPI(Resource_ListAPI):
    """location list and create resource."""

    def __init__(self):
        """create instance."""
        super(Location_ListAPI, self).__init__()
        self._parser_create.add_argument(
                'name', type=str, location='json',
                help='`name` cannot be blank', required=True)


class Vendor_API(Resource_API):
    """vendor resource for rest endpoints."""

    def __init__(self):
        """create instance."""
        super(Vendor_API, self).__init__()
        self._parser_update.add_argument(
                'name', type=str, location='json',
                store_missing=False)
        self._parser_update.add_argument(
                'model', type=str, location='json',
                store_missing=False)


class Vendor_ListAPI(Resource_ListAPI):
    """vendor list and create resource."""

    def __init__(self):
        """create instance."""
        super(Vendor_ListAPI, self).__init__()
        self._parser_create.add_argument(
                'name', type=str, location='json',
                help='`name` cannot be blank', required=True)
        self._parser_create.add_argument(
                'model', type=str, location='json',
                help='`model` cannot be blank', required=True)


class MhCluster_API(Resource_API):
    """cluster resource for rest endpoints."""

    def __init__(self):
        """create instance."""
        super(MhCluster_API, self).__init__()
        self._parser_update.add_argument(
                'name', type=str, location='json',
                store_missing=False)
        self._parser_update.add_argument(
                'admin_host', type=str, location='json',
                store_missing=False)
        self._parser_update.add_argument(
                'env', type=str, location='json',
                store_missing=False)


class MhCluster_ListAPI(Resource_ListAPI):
    """cluster list and create resource."""

    def __init__(self):
        """create instance."""
        super(MhCluster_ListAPI, self).__init__()
        self._parser_create.add_argument(
                'name', type=str, location='json',
                help='`name` cannot be blank', required=True)
        self._parser_create.add_argument(
                'admin_host', type=str, location='json',
                help='`admin_host` cannot be blank', required=True)
        self._parser_create.add_argument(
                'env', type=str, location='json',
                help='`env` cannot be blank', required=True)


class Role_API(Resource):
    """role resource for rest endpoints."""

    def __init__(self):
        """create instance."""
        super(Role_API, self).__init__()

        self._parser_update = reqparse.RequestParser()


    def get(self, r_id):
        resource = Role.query.filter_by(ca_id=r_id).first()
        abort_404_if_resource_none(resource, 'Role[%i]' % r_id)
        return marshal(resource, RESOURCE_FIELDS['Role']), 200


    def put(self, r_id):
        abort(405, message='not allowed to update')


    def delete(self, r_id):
        resource = Role.query.filter_by(ca_id=r_id).first()
        if resource:
            resource.delete()
        return '', 204


class Role_ListAPI(Resource):
    """role resource for rest api: get list, post."""

    def __init__(self):
        """create instance."""
        super(Role_ListAPI, self).__init__()

        self._parser_create = reqparse.RequestParser()
        self._parser_create.add_argument(
                'name', type=str,
                location='json', required=True,
                help='`name` cannot be blank')
        self._parser_create.add_argument(
                'ca_id', type=int,
                location='json', required=True,
                help='`ca_id` cannot be blank')
        self._parser_create.add_argument(
                'location_id', type=int,
                location='json', required=True,
                help='`location_id` cannot be blank')
        self._parser_create.add_argument(
                'cluster_id', type=int,
                location='json', required=True,
                help='`cluster_id` cannot be blank')


    def get(self):
        resource_list = Role.query.all()
        return marshal(resource_list, RESOURCE_FIELDS['Role']), 200

    def post(self):
        args = self._parser_create.parse_args()
        try:
            resource = Role.create(**args)
        except (AssociationError,
                InvalidCaRoleError,
                InvalidEmptyValueError,
                InvalidOperationError) as e:
            abort(400, message=e.message)
        else:
            return marshal(resource, RESOURCE_FIELDS['Role']), 201

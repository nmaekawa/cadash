# -*- coding: utf-8 -*-
"""rest resources inventory section.

ATT: rest api must be secured by nginx with at least basic auth!
"""

from flask_login import login_required
from flask_restful import Resource
from flask_restful import abort
from flask_restful import fields
from flask_restful import marshal
from flask_restful import reqparse
import json

from cadash.inventory.dce_models import DceConfigForEpiphanCa
from cadash.inventory.dce_models import DceConfigForEpiphanCaFactory
from cadash.inventory.errors import AssociationError
from cadash.inventory.errors import DuplicateAkamaiStreamIdError
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
from cadash.inventory.errors import MissingConfigSettingError
from cadash.inventory.errors import MissingVendorError
from cadash.inventory.models import AkamaiStreamingConfig
from cadash.inventory.models import Ca
from cadash.inventory.models import EpiphanChannel
from cadash.inventory.models import EpiphanRecorder
from cadash.inventory.models import Location
from cadash.inventory.models import MhCluster
from cadash.inventory.models import MhpearlConfig
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
            'datetime_ntpserver': fields.String,
            'datetime_timezone': fields.String,
            'firmware_version': fields.String,
            'maintenance_permanent_logs': fields.Boolean,
            'source_deinterlacing': fields.Boolean,
            'touchscreen_allow_recording': fields.Boolean,
            'touchscreen_timeout_secs': fields.Integer,
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
            'primary_pr_vconnector': fields.String,
            'primary_pr_vinput': fields.String,
            'primary_pn_vconnector': fields.String,
            'primary_pn_vinput': fields.String,
            'secondary_pr_vconnector': fields.String,
            'secondary_pr_vinput': fields.String,
            'secondary_pn_vconnector': fields.String,
            'secondary_pn_vinput': fields.String,
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
        'AkamaiStreamingConfig': {
            'id': fields.Integer,
            'name': fields.String,
            'comment': fields.String,
            'stream_id': fields.String,
            'stream_user': fields.String,
            'stream_password': fields.String,
            'primary_url_jinja2_template': fields.String,
            'secondary_url_jinja2_template': fields.String,
            'stream_name_jinja2_template': fields.String,
        },
        'EpiphanRecorder': {
            'id': fields.Integer,
            'recorder_id_in_device': fields.Integer,
            'name': fields.String,
            'output_format': fields.String,
            'size_limit_in_kbytes': fields.Integer,
            'time_limit_in_minutes': fields.Integer,
            'channels': fields.List(fields.String),
        },
        'EpiphanChannel': {
            'id': fields.Integer,
            'channel_id_in_device': fields.Integer,
            'name': fields.String,
            'stream_id': fields.String(
                attribute='stream_cfg.stream_id'),
            'primary_url_jinja2_template': fields.String(
                attribute='stream_cfg.primary_url_jinja2_template'),
            'secondary_url_jinja2_template': fields.String(
                attribute='stream_cfg.secondary_url_jinja2_template'),
            'stream_name_jinja2_template': fields.String(
                attribute='stream_cfg.stream_name_jinja2_template'),
            'audio': fields.Boolean,
            'audiobitrate': fields.Integer,
            'audiochannels': fields.String,
            'audiopreset': fields.String,
            'autoframesize': fields.Boolean,
            'codec': fields.String,
            'fpslimit': fields.Integer,
            'framesize': fields.String,
            'vbitrate': fields.Integer,
            'vencpreset': fields.String,
            'vkeyframeinterval': fields.Integer,
            'vprofile': fields.String,
            'source_layout': fields.String
        },
        'MhpearlConfig': {
            'id': fields.Integer,
            'comment': fields.String,
            'mhpearl_version': fields.String,
            'file_search_range_in_sec': fields.Integer,
            'update_frequency_in_sec': fields.Integer,
        },
}
UPDATEABLE_FIELDS = {
        'EpiphanChannel': EpiphanChannel.updateable_fields,
        'EpiphanRecorder': EpiphanRecorder.updateable_fields,
        'Vendor': Vendor.updateable_fields,
        'Location': Location.updateable_fields,
}


def register_resources(api):
    """add resources to rest-api."""

    api.add_resource(
            MhpearlConfig_API,
            '/api/inventory/cas/<int:r_id>/mhpearl',
            endpoint='api_ca_mhpearl')
    api.add_resource(
            EpiphanChannel_API,
            '/api/inventory/cas/<int:r_id>/channels/<string:r_name>',
            endpoint='api_ca_channel')
    api.add_resource(
            EpiphanChannel_ListAPI,
            '/api/inventory/cas/<int:r_id>/channels/',
            endpoint='api_ca_channellist')
    api.add_resource(
            EpiphanRecorder_API,
            '/api/inventory/cas/<int:r_id>/recorders/<string:r_name>',
            endpoint='api_ca_recorder')
    api.add_resource(
            EpiphanRecorder_ListAPI,
            '/api/inventory/cas/<int:r_id>/recorders/',
            endpoint='api_ca_recorderlist')
    api.add_resource(
            DceCaConfig_API,
            '/api/inventory/cas/<int:r_id>/config', endpoint='api_ca_config')
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
    api.add_resource(
            AkamaiStreamingConfig_API,
            '/api/inventory/streamcfgs/<int:r_id>', endpoint='api_streamcfg')
    api.add_resource(
            AkamaiStreamingConfig_ListAPI,
            '/api/inventory/streamcfgs', endpoint='api_streamcfglist')


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
                DuplicateAkamaiStreamIdError,
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


class ResourceConfig_API(Resource_API):
    """base for resource with config rest api put.

    naomi 12oct16: resources with config are treated by rest endpoints
    as having the configs in the same model entity.
    for now, a new config with default values is created when the
    corresponding resource is created. changing a config value requires
    a PUT request to update the ResourceConfig.
    """

    def put(self, r_id):
        """override to deal with resource config fields."""
        resource = self._resource_model_class.get_by_id(r_id)
        abort_404_if_resource_none(
                resource,
                '%s[%i]' % (self._resource_model_class_name, r_id))

        args = self._parser_update.parse_args()
        kwargs = {}
        for key in UPDATEABLE_FIELDS[self._resource_model_class_name]:
            if key in args.keys():
                kwargs[key] = args[key]
        try:
            resource.update(**kwargs)
        except (AssociationError,
                DuplicateAkamaiStreamIdError,
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

        kwargs = {}
        for key in UPDATEABLE_FIELDS['{}Config'.format(
            self._resource_model_class_name)]:
            if key in args.keys():
                kwargs[key] = args[key]
        try:
            resource.config.update(**kwargs)
        except (AssociationError,
                DuplicateAkamaiStreamIdError,
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
                DuplicateAkamaiStreamIdError,
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
        self._parser_update.add_argument(
                'primary_pr_vconnector', type=str, location='json',
                store_missing=False)
        self._parser_update.add_argument(
                'primary_pr_vinput', type=str, location='json',
                store_missing=False)
        self._parser_update.add_argument(
                'primary_pn_vconnector', type=str, location='json',
                store_missing=False)
        self._parser_update.add_argument(
                'primary_pn_vinput', type=str, location='json',
                store_missing=False)
        self._parser_update.add_argument(
                'secondary_pr_vconnector', type=str, location='json',
                store_missing=False)
        self._parser_update.add_argument(
                'secondary_pr_vinput', type=str, location='json',
                store_missing=False)
        self._parser_update.add_argument(
                'secondary_pn_vconnector', type=str, location='json',
                store_missing=False)
        self._parser_update.add_argument(
                'secondary_pn_vinput', type=str, location='json',
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
        self._parser_update.add_argument(
            'datetime_ntpserver', type=str, location='json',
            store_missing=False)
        self._parser_update.add_argument(
            'datetime_timezone', type=str, location='json',
            store_missing=False)
        self._parser_update.add_argument(
            'firmware_version', type=str, location='json',
            store_missing=False)
        self._parser_update.add_argument(
            'maintenance_permanent_logs', type=bool, location='json',
            store_missing=False)
        self._parser_update.add_argument(
            'source_deinterlacing', type=bool, location='json',
            store_missing=False)
        self._parser_update.add_argument(
            'touchscreen_allow_recording', type=bool, location='json',
            store_missing=False)
        self._parser_update.add_argument(
            'touchscreen_timeout_secs', type=int, location='json',
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


class AkamaiStreamingConfig_API(Resource_API):
    """akamai streaming config resource."""
    def put(self, r_id):
        """override to disable updates in akamai streaming config."""
        abort(405, message='not allowed to update')


class AkamaiStreamingConfig_ListAPI(Resource_ListAPI):
    """akamai streaming config list and create resource."""

    def __init__(self):
        """create instance."""
        super(AkamaiStreamingConfig_ListAPI, self).__init__()
        self._parser_create.add_argument(
                'name', type=str, required=True,
                help='`name` cannot be blank', location='json')
        self._parser_create.add_argument(
                'comment', type=str, required=False,
                store_missing=False, location='json')
        self._parser_create.add_argument(
                'stream_id', type=str, required=True,
                help='`stream_id` cannot be blank', location='json')
        self._parser_create.add_argument(
                'stream_user', type=str, required=True,
                help='`stream_user` cannot be blank', location='json')
        self._parser_create.add_argument(
                'stream_password', type=str, required=True,
                help='`stream_password` cannot be blank', location='json')
        self._parser_create.add_argument(
                'primary_url_jinja2_template', type=str, required=False,
                store_missing=False, location='json')
        self._parser_create.add_argument(
                'secondary_url_jinja2_template', type=str, required=False,
                store_missing=False, location='json')
        self._parser_create.add_argument(
                'stream_name_jinja2_template', type=str, required=False,
                store_missing=False, location='json')


class DceCaConfig_API(Resource):
    """configuration for a dce capture agent."""

    def __init__(self):
        """create instance."""
        super(DceCaConfig_API, self).__init__()

    def get(self, r_id):
        """override to pull dce config."""
        role_cfg = DceConfigForEpiphanCaFactory.retrieve(r_id)
        abort_404_if_resource_none(
                resource=role_cfg, resource_id='CaConfig[{}]'.format(r_id))
        try:
            resource = role_cfg.epiphan_dce_config
        except MissingConfigSettingError as e:
            abort(400, message='CA({}) config error: {}'.format(r_id, e.message))
        return resource, 200


    def put(self, r_id):
        """updates in ca configuration."""
        abort(405, message='not allowed to update')



class EpiphanRecorder_API(Resource_API):
    """recorders configured in a ca."""

    def __init__(self):
        """create instance."""
        super(EpiphanRecorder_API, self).__init__()
        self._parser_update.add_argument(
                'recorder_id_in_device', type=int,
                location='json', store_missing=False)
        self._parser_update.add_argument(
                'output_format', type=str,
                location='json', store_missing=False)
        self._parser_update.add_argument(
                'size_limit_in_kbytes', type=int,
                location='json', store_missing=False)
        self._parser_update.add_argument(
                'time_limit_in_minutes', type=int,
                location='json', store_missing=False)
        self._parser_update.add_argument(
                'channels', type=list,
                location='json', store_missing=False)


    @classmethod
    def find_recorder(cls, ca_id, recorder_name):
        """given a capture agent, find its recorder by name."""
        ca = Ca.get_by_id(ca_id)
        if ca is not None:
            if ca.role is not None and ca.role.config is not None:
                for rec in ca.role.config.recorders:
                    if rec.name == recorder_name:
                        return rec
        return None

    def get(self, r_id, r_name):
        rec = EpiphanRecorder_API.find_recorder(r_id, r_name)
        abort_404_if_resource_none(
                rec, 'EpiphanRecorder({}) for ca({}) not found.'.format(
                    r_name, r_id))
        return marshal(
                rec, RESOURCE_FIELDS['EpiphanRecorder']), 200


    def put(self, r_id, r_name):
        rec = EpiphanRecorder_API.find_recorder(r_id, r_name)
        abort_404_if_resource_none(
                rec, 'EpiphanRecorder({}) for ca({}) not found.'.format(
                    r_name, r_id))

        args = self._parser_update.parse_args()
        try:
            rec.update(**args)
        except (
                DuplicateEpiphanRecorderError,
                DuplicateEpiphanRecorderIdError,
                InvalidOperationError) as e:
            abort(400, message=e.message)
        else:
            return marshal(
                    rec, RESOURCE_FIELDS['EpiphanRecorder']), 200

    def delete(self, r_id):
        rec = EpiphanRecorder_API.find_recorder(r_id, r_name)
        if not rec:
            rec.delete()
        return '', 204


class EpiphanRecorder_ListAPI(Resource_ListAPI):
    """recorder list configured for a ca."""

    def __init__(self):
        """create instance."""
        super(EpiphanRecorder_ListAPI, self).__init__()
        self._parser_create.add_argument(
                'name', type=str, required=True,
                help='`name` cannot be blank', location='json')


    def get(self, r_id):
        ca = Ca.get_by_id(r_id)
        if ca is not None:
            if ca.role is not None and ca.role.config is not None:
                return marshal(
                    ca.role.config.recorders,
                    RESOURCE_FIELDS['EpiphanRecorder']), 200
        abort(404, 'EpiphanRecorders not found for ca({})'.format(r_id))


    def post(self, r_id):
        ca = Ca.get_by_id(r_id)
        if ca is not None:
            if ca.role is not None and ca.role.config is not None:
                args = self._parser_create.parse_args()
                try:
                    recorder = EpiphanRecorder.create(
                            name=args['name'], epiphan_config=ca.role.config)
                except DuplicateEpiphanRecorderError as e:
                    abort(400, message=e.message)
                else:
                    return marshal(
                            recorder,
                            RESOURCE_FIELDS['EpiphanRecorder']), 200
        abort(404, 'Capture Agent({}) not found'.format(r_id))


class EpiphanChannel_API(Resource_API):
    """channel configured in a ca."""

    def __init__(self):
        """create instance."""
        super(EpiphanChannel_API, self).__init__()
        self._parser_update.add_argument(
                'channel_id_in_device', type=int,
                location='json', store_missing=False)
        self._parser_update.add_argument(
                'stream_cfg_id', type=int,
                location='json', store_missing=False)
        self._parser_update.add_argument(
                'audio', type=bool,
                location='json', store_missing=False)
        self._parser_update.add_argument(
                'audiobitrate', type=int,
                location='json', store_missing=False)
        self._parser_update.add_argument(
                'audiochannels', type=str,
                location='json', store_missing=False)
        self._parser_update.add_argument(
                'audiopreset', type=str,
                location='json', store_missing=False)
        self._parser_update.add_argument(
                'autoframesize', type=bool,
                location='json', store_missing=False)
        self._parser_update.add_argument(
                'codec', type=str,
                location='json', store_missing=False)
        self._parser_update.add_argument(
                'fpslimit', type=int,
                location='json', store_missing=False)
        self._parser_update.add_argument(
                'framesize', type=str,
                location='json', store_missing=False)
        self._parser_update.add_argument(
                'vbitrate', type=int,
                location='json', store_missing=False)
        self._parser_update.add_argument(
                'vencpreset', type=str,
                location='json', store_missing=False)
        self._parser_update.add_argument(
                'vkeyframeinterval', type=int,
                location='json', store_missing=False)
        self._parser_update.add_argument(
                'vprofile', type=str,
                location='json', store_missing=False)
        self._parser_update.add_argument(
                'source_layout', type=str,
                location='json', store_missing=False)


    @classmethod
    def find_channel(cls, ca_id, channel_name):
        """given a capture agent, find a channel by name."""
        ca = Ca.get_by_id(ca_id)
        if ca is not None:
            if ca.role is not None and ca.role.config is not None:
                for chan in ca.role.config.channels:
                    if chan.name == channel_name:
                        return chan
        return None

    def get(self, r_id, r_name):
        chan = EpiphanChannel_API.find_channel(r_id, r_name)
        abort_404_if_resource_none(
                chan, 'EpiphanChannel({}) for ca({}) not found.'.format(
                    r_name, r_id))
        return marshal(
                chan, RESOURCE_FIELDS['EpiphanChannel']), 200


    def put(self, r_id, r_name):
        chan = EpiphanChannel_API.find_channel(r_id, r_name)
        abort_404_if_resource_none(
                chan, 'EpiphanChannel({}) for ca({}) not found.'.format(
                    r_name, r_id))

        args = self._parser_update.parse_args()
        try:
            chan.update(**args)
        except (
                DuplicateEpiphanChannelError,
                DuplicateEpiphanChannelIdError,
                InvalidJsonValueError,
                InvalidOperationError) as e:
            abort(400, message=e.message)
        else:
            return marshal(
                    chan, RESOURCE_FIELDS['EpiphanChannel']), 200

    def delete(self, r_id):
        chan = EpiphanChannel_API.find_channel(r_id, r_name)
        if not chan:
            chan.delete()
        return '', 204


class EpiphanChannel_ListAPI(Resource_ListAPI):
    """channel list configured for a ca."""

    def __init__(self):
        """create instance."""
        super(EpiphanChannel_ListAPI, self).__init__()
        self._parser_create.add_argument(
                'name', type=str, required=True,
                help='`name` cannot be blank', location='json')

    def get(self, r_id):
        ca = Ca.get_by_id(r_id)
        if ca is not None:
            if ca.role is not None and ca.role.config is not None:
                return marshal(
                    ca.role.config.channels,
                    RESOURCE_FIELDS['EpiphanChannel']), 200
        abort(404, 'EpiphanChannels not found for ca({})'.format(r_id))


    def post(self, r_id):
        ca = Ca.get_by_id(r_id)
        if ca is not None:
            if ca.role is not None and ca.role.config is not None:
                args = self._parser_create.parse_args()
                try:
                    channel = EpiphanChannel.create(
                            name=args['name'], epiphan_config=ca.role.config)
                except DuplicateEpiphanChannelError as e:
                    abort(400, message=e.message)
                else:
                    return marshal(
                            channel,
                            RESOURCE_FIELDS['EpiphanChannel']), 200
        abort(404, 'Capture Agent({}) not found'.format(r_id))



class MhpearlConfig_API(Resource_API):
    """mhpearl configs in a ca."""

    def __init__(self):
        """create instance."""
        super(MhpearlConfig_API, self).__init__()
        self._parser_update.add_argument(
                'comment', type=str,
                location='json', store_missing=False)
        self._parser_update.add_argument(
                'mhpearl_version', type=str,
                location='json', store_missing=False)
        self._parser_update.add_argument(
                'file_search_range_in_sec', type=int,
                location='json', store_missing=False)
        self._parser_update.add_argument(
                'update_frequency_in_sec', type=int,
                location='json', store_missing=False)


    def get(self, r_id):
        ca = Ca.get_by_id(r_id)
        if ca is not None and ca.role is not None and ca.role.config is not None:
            return marshal(
                ca.role.config.mhpearl, RESOURCE_FIELDS['MhpearlConfig']), 200
        abort(404, 'Mhpearl Config not found for ca({})'.format(r_id))


    def put(self, r_id):
        ca = Ca.get_by_id(r_id)
        if ca is not None and ca.role is not None and ca.role.config is not None:
            mhpearl = ca.role.config.mhpearl
            args = self._parser_update.parse_args()
            try:
                mhpearl.update(**args)
            except InvalidOperationError as e:
                abort(400, message=e.message)
            else:
                return marshal(
                        mhpearl, RESOURCE_FIELDS['MhpearlConfig']), 200
        abort(404, 'Mhpearl Config not found for ca({})'.format(r_id))


    def delete(self, r_id):
        abort(405, message='not allowed to delete')


    def post(self, r_id):  # is this needed?
        abort(405, message='not allowed to create')


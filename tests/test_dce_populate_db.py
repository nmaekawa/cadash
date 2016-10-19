# -*- coding: utf-8 -*-
"""populate cadash db with info from dce custom json."""
import boto3
from botocore.exceptions import ClientError
import json
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError

from epipearl import Epipearl

from cadash.inventory.models import Ca
from cadash.inventory.models import EpiphanChannel
from cadash.inventory.models import EpiphanRecorder
from cadash.inventory.models import Location
from cadash.inventory.models import LocationConfig
from cadash.inventory.models import MhCluster
from cadash.inventory.models import MhpearlConfig
from cadash.inventory.models import Role
from cadash.inventory.models import RoleConfig
from cadash.inventory.models import Vendor
from cadash.utils import pull_data

CA_BUCKET = 'ca-settings'

class AwsS3(object):

    def __init__(self, bucket_name):
        self.s3 = boto3.resource('s3')
        self.s3.meta.client.head_bucket(Bucket=bucket_name)
        self.bucket = self.s3.Bucket(bucket_name)

    @property
    def bucket_name(self):
        return self.bucket.name

    def get_device_settings(self, device_name):
        key = '{}.json'.format(device_name)
        obj = self.bucket.Object(key).get()
        return obj['Body'].read()

    def set_device_settings(self, device_name, settings):
        self.bucket.put_object(Key='{}.json'.format(device_name), Body=settings)

    def get_device_list(self):
        obj_list = self.bucket.objects.all()
        device_list = []
        for obj in obj_list:
            if obj.key.endswith('.json'):
                (dev, ext) = obj.key.split('.')
                device_list.append(dev)
        return device_list


def app():
    """An application."""
    config = Config(environment='dev', login_disabled=True)
    # TODO: get db name from command line
    config.DB_NAME = 'something_different.db'
    _app = create_app(config)
    ctx = _app.test_request_context()
    ctx.push()
    yield _app
    ctx.pop()


def db(app):
    """A database for app."""
    _db.app = app
    with app.app_context():
        _db.create_all()
    yield _db
    _db.session.close() # Explicitly close DB connection
    _db.drop_all()


def pull_settings_from_s3(app):
    try:
        s3 = AwsS3(CA_BUCKET)
    except ClientError as e:
        print('error connecting to s3: {}'.format(e.message))
        exit(1)

    dev_name_list = s3.get_device_list()
    settings = {}
    for dev_name in dev_name_list:
        datastring = s3.get_device_settings(dev_name)
        if datastring is None:
            print('check settings for device({})'.format(dev_name))
            exit(2)
        cfg = json.loads(datastring)
        print('ca({}) in {}'.format(cfg['ca_name_id'], cfg['location_name_id']))
        settings[dev_name] = cfg
    return settings


def test_list_s3_bucket():
    try:
        s3 = AwsS3(CA_BUCKET)
    except ClientError as e:
        print('error connecting to s3: {}'.format(e.message))
        exit(1)
    for obj in s3.get_device_list():
        print(obj)

    assert True == False


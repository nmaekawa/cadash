# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
import json
import logging
import time

from flask import Blueprint
from flask import current_app
from flask import flash
from flask import render_template
from flask import request
from flask_login import login_required

from cadash import __version__ as app_version
from cadash.utils import pull_data
from cadash.redunlive.data_masseuse import map_redunlive_ca_loc


blueprint = Blueprint(
        'redunlive', __name__,
        static_folder='../static',
        url_prefix='/redunlive')


def prep_redunlive_data():
    json_text = pull_data(
            current_app.config['CA_STATS_JSON_URL'],
            creds={
                'user': current_app.config['CA_STATS_USER'],
                'pwd': current_app.config['CA_STATS_PASSWD']
                })
    return map_redunlive_ca_loc(json.loads(json_text))


@blueprint.route('/', methods=['GET', 'POST'])
@login_required
def home():
    """redunlive home page: all locations."""
    # example of logger
    logger = logging.getLogger(__name__)
    logger.info('----- this is a log message from app: %s' % __name__)

    # init location-ca list
    data = prep_redunlive_data()
    locations = sorted(data['all_locations'].values(), key=lambda t: t.id)

    if current_app.config['ENV'] == 'dev' \
            and 'loc_id' in request.form.keys():
        flash('form input loc-id %s' % request.form['loc_id'])
        logger.debug('request.form loc-id is %s' % (request.form['loc_id']))

    # form submitted
    if request.method == 'POST':
        # get location to toggle
        location = data['all_locations'][request.form['loc_id']]

        if location.active_livestream is None:
            pass  # do not start/stop if no active streaming!
        else:
            # toggling from backup to primary requires a start over
            if request.form['active_device'] == 'primary':
                # start primary streaming
                location.primary_ca.write_live_status('6')
                time.sleep(2)
                # stop backup streaming so akamai detect that for sure
                location.secondary_ca.write_live_status('0')
                time.sleep(1)
                # start backup streaming again
                location.secondary_ca.write_live_status('6')
            else:
                # make sure secondary is streaming
                location.secondary_ca.write_live_status('6')
                time.sleep(2)
                # stop streaming primary
                location.primary_ca.write_live_status('0')
                time.sleep(1)

            # make sure we have the device status
            location.primary_ca.sync_live_status()
            location.secondary_ca.sync_live_status()
        # end -- there is active livestreaming

    return render_template(
            'redunlive/home.html', version=app_version, locations=locations)

# @blueprint.route('/logout/')
# def logout():
#    """Logout."""
#    logout_user()
#    flash('You are logged out.', 'info')
#    return redirect(url_for('public.home'))

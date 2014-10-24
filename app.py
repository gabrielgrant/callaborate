#!/usr/bin/env python

"""
Python source code

replace this with a description of the code and write the code below this text.
"""
from datetime import datetime, timedelta
import hashlib
import os
import urllib
from functools import wraps

from flask import Flask, jsonify, request
from flask.ext.cors import cross_origin
import requests

import calls
import config
import db
from db import store_event, get_next_callee, CALLEES

app = Flask(__name__, static_folder='static', static_url_path='')

SECRET = config.get('SECRET')

def create_key(index):
    """Hash a secret to create a key signature for an index"""
    s = hashlib.sha1()
    s.update('{}:{}'.format(SECRET, index))
    return s.hexdigest()

def check_key(index, key):
    return create_key(index) == key


def timeblock(inner_fn):
    @wraps(inner_fn)
    def outer_fn(*args, **kwargs):
        utc_offset_hours = int(config.get('TIMEZONE_UTC_OFFSET'))
        utc_offset = timedelta(seconds=60*60*utc_offset_hours)
        hour = (datetime.utcnow() + utc_offset).time().hour
        call_time_start = int(config.get('CALL_TIME_START', 9))  # open at 9am by default
        call_time_end = int(config.get('CALL_TIME_END', 21))  # close at 9pm by default
        if hour < call_time_end and hour >= call_time_start:
            return inner_fn(*args, **kwargs)
        try:
            request_data = request.get_json()
        except:
            request_data = {}
        event_data = {
            'path': request.path,
            'endpoint': request.endpoint,
            'request_data': request_data
        }
        store_event('after_hours', event_data)
        return jsonify(error='after_hours')
    return outer_fn




def build_callee(raw_callee):
    r = lambda x: x
    t = lambda x: x.title()
    mapping = {
        'first_name': ('firstName', t),
        'last_name': ('lastName', t),
        'residential_city': ('residentialCity', r),
    }
    return dict((k_out,l(raw_callee[k_in])) for k_in, (k_out, l) in mapping.iteritems())

def get_callee():
    index, raw_callee = get_next_callee()
    callee = build_callee(raw_callee)
    callee['id'] = index
    callee['key'] = create_key(index)
    return callee, raw_callee['phone']

@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.route('/call_count')
@cross_origin()
def call_count():
    return db.count_calls()

@app.route('/leaderboard')
@cross_origin()
def leaderboard():
    return jsonify(leaderboard=db.get_leaderboard(), total_called=db.count_calls())

@app.route('/sign_in', methods=['POST'])
@timeblock
def sign_in():
    # log signin
    data = request.get_json()
    
    if data:
        store_event('sign_in', data)
    return 'sign_in success'
    #TODO return failure message if calling out of hours
    # add time-ban decorator to all methods

@app.route('/connect_caller', methods=['POST'])
@timeblock
def connect_caller():
    data = request.get_json()
    data['session_id'] = calls.make_call(data['phoneNumber'])
    store_event('connect_caller', data)
    return jsonify(sessionId=data['session_id'])

@app.route('/connect_callee', methods=['POST'])
@timeblock
def connect_callee():
    data = request.get_json()
    callee, phone = get_callee()
    if os.environ.get('PRODUCTION') is None:
        phone = config.get('TEST_CALLEE')
    calls.send_signal(data['sessionId'], phone)
    
    event_data = {'caller': data, 'callee': callee, 'phone': phone}
    store_event('connect_callee', event_data)
    return jsonify(callee)

@app.route('/save_call', methods=['POST'])
def save_call():
    raw_data = request.get_json()
    # check key
    callee_id = raw_data['callee']['id']
    callee_key = raw_data['callee']['key']
    if not check_key(callee_id, callee_key):
        return 'failed'
    source_data = {
        'callee': CALLEES[callee_id],
        'caller': raw_data['caller'],
        'call': raw_data['callInfo'],
    }
    call_data_config = config.get('CALL_DATA_FORM')
    data = {}
    for field_source_name, field_source_values in call_data_config['fields'].iteritems():
        for k,v in field_source_values.iteritems():
            data[k] = source_data[field_source_name].get(v, '')
    url = call_data_config['url']
    requests.post(url, data=data)
    store_event('save_call', {'raw_data': raw_data, 'saved_data': data})
    return 'saved'

if __name__ == "__main__":
    port = os.environ.get('PORT')
    if port:
        port = int(port)
    app.run(debug=True, host='0.0.0.0', port=port)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

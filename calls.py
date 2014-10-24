#!/usr/bin/env python

"""
Python source code

replace this with a description of the code and write the code below this text.
"""
import json
import time
import requests

import config

JSON_HEADERS = {'Content-type': 'application/json', 'Accept': 'application/json'}

def make_call(number):
    url = 'https://api.tropo.com/1.0/sessions'
    data = {
        'token': config.get('TROPO_VOICE_API_KEY'),
        'number': number,
    }
    r = requests.post(url, data=json.dumps(data), headers=JSON_HEADERS)
    return r.json['id']  # session_id

def send_signal(session_id, signal):
    session_id = session_id.strip()
    url = 'https://api.tropo.com/1.0/sessions/{}/signals'.format(session_id)
    data = {'signal': signal,}
    r = requests.post(url, data=json.dumps(data), headers=JSON_HEADERS)

if __name__ == '__main__':
    from_number = config.get('TEST_CALL_FROM')
    to_number = config.get('TEST_CALL_TO')
    print 'testing call from %s to %s' % (from_number, to_number)
    session_id = make_call(from_number)
    print 'call established: ', session_id
    raw_input('Press enter to send signal')
    print('sending signal')
    send_signal(session_id, to_number)
    

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

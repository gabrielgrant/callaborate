#!/usr/bin/env python

"""
Utils to interact with the redis DB
"""
import csv
from datetime import datetime
import json
import os

import redis

LOCAL_REDIS = 'redis://localhost:6379/0'
REDIS_URL = os.environ.get('REDISCLOUD_URL', LOCAL_REDIS)
CALLEE_COUNTER_KEY = 'callee_counter'
EVENTS_KEY = 'events'
CALLED_NUMBERS_SET_KEY = 'called_numbers_set'
redis = redis.from_url(REDIS_URL)

def store_event(event_name, data):
    event = dict(
        name=event_name,
        timestamp=datetime.utcnow().isoformat(),
        data=data,
    )
    redis.rpush(EVENTS_KEY, json.dumps(event))

def count_calls():
    return redis.get(CALLEE_COUNTER_KEY)


CALLEES = list(csv.DictReader(open('data/callees.csv')))

def get_next_callee():
    index = redis.incr(CALLEE_COUNTER_KEY) - 1
    callee = CALLEES[index]
    if redis.sismember(CALLED_NUMBERS_SET_KEY, callee['phone']):
        store_event('skipped_repeat_number', callee)
        return get_next_callee()
    else:
        redis.sadd(CALLED_NUMBERS_SET_KEY, callee['phone'])
        return index, callee

def get_events():
    events = {}
    for e in redis.lrange("events", 0, -1):
        e = json.loads(e)
        events.setdefault(e['name'], []).append(e)
    return events

def coalesce_dicts(signins):
    user = {}
    keys = set()
    keys.update(*signins)
    for k in keys:
        for s in signins:
            if s.get(k):
                user[k] = s.get(k)
    return user

def sort_dicts_by_key(items, sort_key, mutate=lambda k, v: k):
    retval = {}
    for i in items:
        key = mutate(i.get(sort_key), i)
        retval.setdefault(key, []).append(i)
    return retval

def get_calls_by_phone():
    events = get_events()
    call_data = [e['data']['raw_data'] for e in events['save_call']]
    caller_data = [e['data']['raw_data']['caller'] for e in events['save_call']]
    def remove_dashes(k, v):
        if k:
            return k.replace('-', '')
        else:
            return k
    return sort_dicts_by_key(caller_data, 'phoneNumber', mutate=remove_dashes)

def get_full_leaderboard():
    calls_by_phone = get_calls_by_phone()
    leaders = sorted([(len(v), k) for k,v in calls_by_phone.items()], reverse=True)
    users = [coalesce_dicts(calls_by_phone[k]) for v,k in leaders]
    full_leaderboard = [dict(calls=v, **u) for u, (v,k) in zip(users, leaders)]
    for l in full_leaderboard: del l['sessionId']
    return full_leaderboard

def get_leaderboard():
    users = get_full_leaderboard()
    names = ['{} {}.'.format(u.get('firstName', 'Anonymous').title(), u.get('lastName', 'Badger')[:1].upper()) for u in users]
    return [{'name': n, 'calls': u['calls']} for n, u in zip(names, users)]

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

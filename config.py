#!/usr/bin/env python

"""
Load app config

Looks for config vars in the environment, falls back to config.json as a base
"""

import json
import os

try:
    CONFIG = json.load(open('config.json'))
except IOError:
    CONFIG = {}

def get(name, default=None, optional=False):
    """ looks for a var in env first, then in config.json """
    var = os.environ.get(name) or CONFIG.get(name)
    if var is None:
        var = default
    if not optional and var is None:
        raise KeyError('No config var named %s found' % name)
    return var

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

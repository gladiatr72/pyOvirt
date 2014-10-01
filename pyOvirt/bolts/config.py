# -*- coding: utf-8 -*-

from __future__ import print_function
import salt.config
import copy

def get_mc():
    '''
    retrieve the ovirt bits from the master config
    YAML:

    ovirt:
        default:
            user: you@yourauthdomain.com
            password: we eats it, precious
            protocol: http(s)
            persist: False
            alias: None
        mananger-01.somedomain.interwebs.com:
            alias: manager-01
            cert: /path/to/CA/cert/for/manager
        fiddler.somedomain.interwebs.com:
            alias: manager-02
            cert: ...
    '''

    return salt.config.minion_config(
            salt.config.DEFAULT_MINION_OPTS['conf_file'])['ovirt']

def default_merge(manager):
    '''
    merge the default bits with the manager-specific ones
    '''
    if 'default' in get_mc():
        mgr = copy.deepcopy(get_mc()['default'])
    else:
        mgr = {}

    mgr.update(get_mc()[manager])

    return mgr


def list_managers():

    retval = {}
    mc = get_mc()
    managers = [ t for t in get_mc() if t != 'default' ]

    for mgr in managers:
        if 'alias' in mc[mgr]:
            alias = mc[mgr]['alias']
        else:
            alias = ''

        retval[mgr] = {'alias' : alias }

    return retval

def get_alias(manager):
    if not manager:
        return False

    config = dict([ (t, get_mc()[t]) for t in get_mc() if t != 'default' ]) 
    alias = [ config[t]['alias'] for t in config if 'alias' in config[t] ]

    if manager in alias:
        return manager
    elif manager in config:
        if 'alias' in  config[manager]:
            return config[manager]['alias']

    return False

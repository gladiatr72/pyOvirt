# -*- coding: utf-8 -*-

from __future__ import print_function
import salt.config
import copy

__all__ = 'get_mc list_managers get_alias check_manager'.split(' ')

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

    if 'alias' in get_mc()[manager]:
        return get_mc()[manager]['alias']
    else:
        return manager


def check_manager(manager):
    if not manager or not get_conn(manager):
        return False
    else:
        return True


# -*- coding: utf-8 -*-

import copy
import logging

from config import default_merge, get_mc
from Auth import ovirtAuth

log = logging.getLogger(__name__)

api = {}

def init_conn(manager):
    if manager not in get_mc():
        try:
            manager = [ t for t in get_mc()
                    if t != 'default'
                        and 'alias' in get_mc()[t]
                        and get_mc()[t]['alias'] == manager ].pop()
        except IndexError as e:
            log.info(e,
                    '{0} is an invalid ovirt manager designation'.format(manager))
            return False

    if manager:
        cfg = default_merge(manager)
    else:
        return False

    cfg_out = copy.deepcopy(cfg)
    cfg_out['password'] = '***'
    log.trace(cfg_out)

    alias = cfg['alias'] if 'alias' in cfg else manager

    if alias in api:
        return api[alias]

    if 'ca_file' in cfg:
        ca_file_ = cfg['ca_file']
    else:
        ca_file_ = ''

    handle = ovirtAuth(
            url='{protocol}://{manager}'.format(
                protocol=cfg['protocol'], manager=manager),
            username=cfg['user'],
            password=cfg['password'],
            ca_file=ca_file_)

    if 'alias' in cfg:
        api[cfg['alias']] = handle

    api[manager] = handle

    return handle

def get_conn(manager):
    if manager in api:
        return api[manager]

    return init_conn(manager)


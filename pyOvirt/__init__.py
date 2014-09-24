
# -*- coding: utf-8 -*-
'''
Work with virtual machines managed by ovirt/RHEV-M

:depends: 
    ovirtsdk 
    wrapt

'''

from __future__ import print_function

import salt.config
import re


__version__ = 0, 0, 1


from .pyOvirt import *

__all__ = [
    'list_vms',
    'list_vms_up',
    'list_vms_down',
    'list_vms_cooking',
]

try:
    import wrapt
    import ovirtsdk.api

    HAS_ALL_IMPORTS = True
except ImportError:
    HAS_ALL_IMPORTS = False

_cfg = salt.config.DEFAULT_MINION_OPTS['conf_file']
_minion_config = salt.config.minion_config(_cfg)

__virtualname__ = 'ovirt'

def __virtual__():
    if HAS_ALL_IMPORTS and 'ovirt' in _minion_config:
        return __virtualname__
    else:
        return False



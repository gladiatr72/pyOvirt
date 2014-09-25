# -*- coding: utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import jinja2
import sys
import os

import salt.utils
import salt.config

from pyOvirt import *

try:
    import wrapt
    import ovirtsdk.api

    HAS_ALL_IMPORTS = True
except ImportError:
    HAS_ALL_IMPORTS = False

_cfg = salt.config.DEFAULT_MINION_OPTS['conf_file']
_minion_config = salt.config.minion_config(_cfg)

__virtualname__ = 'ovirt'

#Set up template environment
JINJA = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        os.path.join(salt.utils.templates.TEMPLATE_DIRNAME, 'ovirt')
    )
)


def __virtual__():
    if HAS_ALL_IMPORTS and 'ovirt' in _minion_config:
        return __virtualname__
    else:
        return False


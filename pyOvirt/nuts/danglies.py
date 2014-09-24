# -*- coding: utf-8 -*-
'''
Work with virtual machines managed by ovirt/RHEV-M

:depends: ovirtsdk python module
'''

# Import python libs
from __future__ import print_function
import logging
import inspect

from .. import bolts
from ..bolts.config import list_managers, get_alias
from ..bolts.connection import get_conn
from ..memdecay import memdecay

log = logging.getLogger(__name__)


def check_manager(manager):
    if not manager or not get_conn(manager):
        return False
    else:
        return True

def _bit_types(handle):
    bit_types = dict([(t, handle.connection.__dict__[t]) 
                       for t in handle.connection.__dict__ 
                       if not t.startswith('_') ])
    return bit_types


def _valid_arg(argument, function):

    if argument in inspect.getargspec(function).args:
        return True
    else:
        return False

@memdecay(decay=30)
def get_bits(*args, **kwargs):
    '''
    required parameters:
        args[0]; string -- type of bits to deal with 
        args[1]; string -- ovirt manager designator
        args[2]; string -- ovirt manager filter expression or ""
        args[3]; int    -- maximum number of result to return or None
            NOTE: if the bit_type list function does not support 'max',
            you will get NOTHING. Most do, but some don't.

    optional parameters:
        args[4]; string --
            'kill' -- kill the @memdecay'd entry for this thing 
                      that you're doing
            'query'-- return seconds til cache expiration
    '''
    
    kwargs = {}

    if len(args) < 4:
        raise TypeError("Insufficient args:\n{0}".format(get_bits.__doc__))

    bit_type = args[0]
    manager = args[1]
    filter_ = args[2]
    max = args[3]
    cmds = args[4:]

    if check_manager(manager):
        handle = get_conn(manager)
    else:
        return False

    if bit_type not in _bit_types(handle):
        raise NameError("No bits by that name here: {0}".format(bit_type))

    bit_funk = _bit_types(handle)[bit_type].list

    if max and 'max' and _valid_arg('max', bit_funk):
        kwargs['max'] = max

    if filter_ and _valid_arg('query', bit_funk):
        kwargs['query'] = filter_


    return bit_funk(**kwargs)

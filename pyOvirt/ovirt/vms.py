# -*- coding: utf-8 -*-

import re

from engine import get_bits
from ..memdecay import memdecay
from ..bolts.config import list_managers, get_alias


def list_vms(manager='', filter=None, max=0):
    ''' Return the names of configured ovirt guests as well as the name of its
    ovirt/rhev-m manager.

    NOTE: An unqualified run can take a number of minutes to return

    Optional Parameters:
        - manager: the manager from which to retrieve the list of guests,
                   otherwise all registered managers will be queried.
                   (see ovirt.list_managers)
        - filter:  uses the ovirt (GUI filter) to execute server-side query
                   filtering. If it works in the GUI, it'll work here.
        - max:     the maximum number of vms to return. Note: This is not a
                   cursor.  Submitting additional requests with identical
                   parameters will yield identical results (unless vms have
                   been added or removed).

                   Querying multiple managers will return (roughly) 'max' in
                   total

    CLI Example::

        salt '*' ovirt.list_vms manager=vman-02.law
        salt '*' ovirt.list_vms manager=vman-02.law max=10
        salt '*' ovirt.list_vms filter='name=dr-* and host=hyper-1-0*.mn'

    '''

    managers = [ get_alias(t) for t in list_managers() if re.search(manager, t) ]

    retval = {}


    if managers:
        max_ = max / len(managers) 
    else:
        max_ = None

    for m in managers:
        retval.update({m: [vm.name for vm in get_bits('vms', m, filter, max_)]})

    return retval


def list_vms_up(**kwargs):
    ''' 
    list_vms_up|down|cooking

    Takes the same parameters as list_vms but appends status elements 
    to the filter to only list guests in the designated state
    '''

    if 'filter' not in kwargs:
        kwargs['filter'] = "status = up"
    else:
        kwargs['filter'] = "{0} and status = up".format(kwargs['filter'])

    return list_vms(**kwargs)

def list_vms_down(**kwargs):
    '''
    list_vms_up|down|cooking

    Takes the same parameters as list_vms but appends status elements 
    to the filter to only list guests in the designated state
    '''

    if 'filter' not in kwargs:
        kwargs['filter'] = "status = down"
    else:
        kwargs['filter'] = "{0} and status = up".format(kwargs['filter'])

    return list_vms(**kwargs)

def list_vms_cooking(**kwargs):
    '''
    list_vms_up|down|cooking

    Takes the same parameters as list_vms but appends status elements 
    to the filter to only list guests in the designated state

    Definition:

    cooking -- in any of the states that are neither up nor down
    '''

    if 'filter' not in kwargs:
        kwargs['filter'] = "status != up and status != down"
    else:
        kwargs['filter'] = "{0} and status = up".format(kwargs['filter'])

    return list_vms(**kwargs)








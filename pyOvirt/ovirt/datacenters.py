# -*- coding: utf-8 -*-

from engine import get_bits
from ..memdecay import memdecay

@memdecay(decay=20)
def list_datacenters(manager='', filter=None, max=None):
    ''' Return the names of configured ovirt datacenters as well as the name of its
    ovirt/rhev-m manager.

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

        salt '*' ovirt.list_datacenters manager=vman-02.law
        salt '*' ovirt.list_datacenters manager=vman-02.law max=10
        salt '*' ovirt.list_datacenters filter='name=dr-* and host=hyper-1-0*.mn'

    '''

    managers = [ get_alias(t) for t in list_managers() if re.search(manager, t) ]

    retval = {}

    for m in managers:
        handle = get_conn(m).connection
        retval.update({m: [datacenter.name for datacenter in get_bits('datacenters', m, filter, max / len(managers))]})

    return retval











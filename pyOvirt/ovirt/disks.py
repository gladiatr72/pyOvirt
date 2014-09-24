# -*- coding: utf-8 -*-

from engine import get_bits
from ..memdecay import memdecay



@memdecay(decay=90)
def _template_disks(manager):
    ''' return list of disks attached to ovirt template objects '''

    return list(chain(*[ t.disks.list() for t in get_bits('templates', manager, None, None)]))

@memdecay(decay=90)
def _vm_disks(manager):
    ''' return list of disks attached to ovirt template objects '''

    return list(chain(*[ t.disks.list() for t in get_bits('vms', manager, None, None)]))


@memdecay(decay=30)
def list_disks(manager='', filter=None, max=None):
    ''' Return the names of configured ovirt disks as well as the name of its
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

        salt '*' ovirt.list_disks manager=vman-02.law
        salt '*' ovirt.list_disks manager=vman-02.law max=10
        salt '*' ovirt.list_disks filter='name=dr-* and host=hyper-1-0*.mn'


    Returns:

    id:
        attached: True
        attached_to: [vm name]
        size: 

    '''

    managers = [ get_alias(t) for t in list_managers() if re.search(manager, t) ]

    disk_data = {}

    for m in managers:
        handle = get_conn(m).connection
        disk_data.update({m: [disk for disk in get_bits('disks', m, filter, max / len(managers))]})

    return retval


@memdecay(decay=180)
def unattached_disks(*args):
    ''' return list of unattached disks
    NOTE: This is kinda slow--use judiciously

    Required paramaters:
    manager = ovirt manager or configured alias (str)

    NOTE: This function does not take multiple managers
    '''

    if manager is not None:
        attached_disks = [ t.id for t in list(chain(_vm_disks(manager), _template_disks(manager))) ]

    return [ disk for disk in get_disks(manager) if disk.id not in attached_disks ]



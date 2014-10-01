# -*- coding: utf-8 -*-

from __future__ import print_function
from time import strftime, localtime, sleep
import logging
from select import select

from ..nuts.danglies import get_bits, check_manager
from ..nuts.PollableQueue import PollableQueue as Queue
from ..memdecay import memdecay
from itertools import chain
from threading import Thread, local

log = logging.getLogger(__name__)



@memdecay(decay=180)
def _template_disks(manager, Q=None):
    ''' return list of disks attached to ovirt template objects '''

    retval =  list(chain(*[ t.disks.list() for t in get_bits('templates', manager, None, None)]))
    log.debug('{0}: {1} results'.format('tmplds', len(retval)))

    if Q:
        Q.put({'tname': 'tmplds', 'payload': retval})
    else:
        return retval

@memdecay(decay=180)
def _vm_disks(manager, Q=None):
    ''' return list of disks attached to ovirt template objects '''

    retval = list(chain(*[ t.disks.list() for t in get_bits('vms', manager, None, None)]))
    log.debug('{0}: {1} results'.format('vmds', len(retval)))

    if Q:
        Q.put({'tname': 'vmds', 'payload': retval})
    else:
        return retval


@memdecay(decay=180)
def _all_disks(manager, Q=None):
    ''' return list of all disks on an ovirt/rhev manager '''

    retval =  get_bits('disks', manager, None, None)

    if Q:
        Q.put({'tname': 'allds', 'payload': retval})
    else:
        return retval


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
    disk_data.update({m: [disk for disk in get_bits('disks', m, filter, max / len(managers))]})

    return retval

@memdecay(decay=180)
def unattached_disks(manager=None):
    ''' return list of unattached disks
    NOTE: This is kinda slow--use judiciously

    Required paramaters:
    manager = ovirt manager or configured alias (str)

    NOTE: This function does not take multiple managers
    '''

    retval = {}

    if not manager:
        log.info('unattached_disks: "manager" argument required')
        return False
    else:
        if check_manager(manager):
            q_vmd = Queue()

            idents = [ 'allds', 'tmplds', 'vmds' ]
            bits = { 'disk': dict([ (id, None) for id in idents]),
                    'thread': dict([ (id, None) for id in idents]),
                    'func': {
                        'allds': _all_disks,
                        'tmplds': _template_disks,
                        'vmds': _vm_disks
                        }
                    }


            for id in idents:
                bits['thread'][id] = Thread(
                    target=bits['func'][id], name=id, args=(manager,), kwargs={'Q': q_vmd})
                bits['thread'][id].setDaemon(daemonic=True)
                bits['thread'][id].start()

            start=localtime()
            while None in bits['disk'].values():
                _ = [ print('{0} {1}'.format(k, len(bits['disk'][k]))) 
                    for k in bits['disk'].keys() 
                        if bits['disk'][k] is not None
                    ]

                rset, wset, eset = select([ q_vmd ], [], [])
                
                if rset:
                    data = q_vmd.get()
                    tname = data['tname']
                    print('{0}: {1}'.format(strftime('%c', localtime()), tname))
                    bits['disk'][tname] = data['payload']

            all_assigned = tuple(chain(bits['disk']['tmplds'], bits['disk']['vmds']))
            assigned_ids = [ t.id for t in all_assigned ]

            return [ disk.id for disk in bits['disk']['allds'] if disk.id not in assigned_ids ]
     



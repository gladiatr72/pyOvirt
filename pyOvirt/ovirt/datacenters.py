# -*- coding: utf-8 -*-

from ..nuts.danglies import get_bits, check_manager
from ..memdecay import memdecay
from ..bolts.connection import get_conn
from ..bolts.config import get_mc, get_alias
import re
import inspect

@memdecay()
def list_datacenters(manager=None, filter=None, max=None):
    ''' Return the names of configured ovirt datacenters as well as the name of its
    ovirt/rhev-m manager.

    Optional Parameters:
        - manager: the manager from which to retrieve the list of guests,
                   otherwise all registered managers will be queried.
                   (see ovirt.list_managers)
        - filter:  uses the ovirt (GUI filter) to execute server-side query
                   filtering. If it works in the GUI, it'll work here.

    CLI Example::

        salt '*' ovirt.list_datacenters manager=vman-02.law
        salt '*' ovirt.list_datacenters manager=vman-02.law max=10
        salt '*' ovirt.list_datacenters filter='name=something'

    '''

    if not manager:
        managers = [ get_alias(m) for m in get_mc().keys() if m != 'default' ]
    else:
        managers = [ get_alias(manager) ]

    retval = {}

    for m in managers:
        retval.update(
                dict([ 
                    (m, [datacenter.name for datacenter in get_bits('datacenters', m, filter, max)]) 
                    ])
                )

    return retval

@memdecay()
def _cap_types(caps):
    return [ re.sub(r'^get_', '', cap) for cap in dir(caps) 
            if cap.startswith('get_') 
            and not cap.endswith('_') ]

@memdecay()
def get_dc_caps(manager=None, name=None, id=None):
    ''' Return an object that provides a path to a data center's 
    capabilities. 
    '''
    handle = check_manager(manager).connection

    if not handle:
        return False

    if name:
        filter='name = {0}'.format(name)
    elif id: 
        filter='id = {0}'.format(id)

    DC=get_bits('datacenters', manager, filter, None)[0]
    DC_VER = ( DC.get_version().get_major(), DC.get_version().get_minor() )
    CAPS = [ cap for cap in handle.capabilities.list() 
                if (cap.get_major(), cap.get_minor()) == DC_VER ][0]
    
    return CAPS


def _is_ovirt_cap_obj(thing):
    re_ovobj = re.compile(r'^<class..ovirtsdk.xml.params')
    in_question = str(type(thing))

    if re_ovobj.search(in_question):
        return True
    else:
        return False

def _derive_prime_key(things):
    ''' 
    find the property of the ovirt object that is common within a collection.
    Collections are lists of ovirt objects.

    Returns a string
    '''

    # the properties/methods/misc bits attached to these objects that are
    # either REST-related or simply not object-specific

    re_keyhunt = re.compile(r'^(export|gds_|[gs]et_|.*class|tz|url|_|.*link|build|factory|href|description|Tag|has)')

    # the potential properties
    targets = [ (n, t.__dict__[n] )
                for t in things 
                for n in dir(t) 
                    if not re_keyhunt.search(n)
                        and t.__dict__[n] is not None
                        and not _is_ovirt_cap_obj(t.__dict__[n]) ]

    keylist = [ t[0] for t in targets]

    keys = list(set(keylist))

    if len(keylist) == 1:
        return keylist[0]
    elif len(keylist) == 0:
        return None
    
    keycount={}

    for k in keys:
        keycount[k] = len([ t for t in keylist if t == k ])

    keymax = max(keycount.values())

    if sum(keycount.values()) / keymax == 1:
        retval = [ k for k in keycount if keycount[k] == keymax ][0]
    else:
        # oops. we have > 1 keys that are present with the same dispersement
        vallist = dict([ (t[1], t[0]) for t in targets ])
        valcount= dict([ (k, 0) for k in keys ])

        for v in vallist:
            valcount[vallist[v]] += 1 

        retval = [ t[0] for t in valcount.items() if t[1] == len(things)][0] 

    return retval

@memdecay()
def get_caps(manager=None, name=None, id=None):
    ''' this hideous thing is how we're getting the acceptable status messages
    for various pieces of ovirt without hard-coding class/subclass and 
    function names. Ovirt is inconsistent enough to break any normal way of
    going about this. I take corrections with grace.

    @Parameters:
        - manager: manager name/alias (str)
        - name: datacenter name (str)
        - id: datacenter id (str)
        - capability: capability key (str)


    . manager and (name or id) are required
    . if capability is None, return all caps

    '''
    
    re_get = re.compile(r'^get_(.*[^_])$')

    caps = get_dc_caps(manager, name, id)

    if not caps:
        return False

    cap_types = _cap_types(caps)
    cap_dict = {}

    capf = caps.__dict__['superclass'].__dict__

    for member in capf:
        if member in cap_types:
            capname = member
            capobject = capf[member]

            if _is_ovirt_cap_obj(capobject):
                if isinstance(capobject.__dict__, list):
                    if _is_ovirt_cap_obj(capobject.__dict__[0]):
                        prime_key = _derive_prime_key(capobject.__dict__) 

                        

                cap_dict.update(capobject.__dict__)
            else:
                cap_dict.update({ capname: capobject})

    return cap_dict

def get_cap(manager=None, name=None, id=None, capability=None):
    if capability:
        retval = get_caps(manager=manager, name=name, id=id)
        if isinstance(retval, list):
            if _is_ovirt_cap_obj(retval[0]):
                retval = [ t.id for t in retval ]
    else:
        return get_caps(manager=manager, name=name, id=id)


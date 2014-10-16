
# -*- coding: utf-8 -*-
'''
Work with virtual machines managed by ovirt/RHEV-M

:depends: 
    ovirtsdk 
    wrapt

'''

__version__ = 0, 0, 1


from .pyOvirt import *

__all__ = [
    'list_vms',
    'list_vms_up',
    'list_vms_down',
    'list_vms_cooking',
    'get_vm',
    'list_disks',
    'unattached_disks',

]



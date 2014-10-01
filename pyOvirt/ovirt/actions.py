# -*- coding: utf-8 -*-

''' 
common action/parameters are found here 

    @p_async: certain ovirt directives can take an async action
'''

from ovirtsdk.xml import params


def p_async():
    return params.Action(async=True)


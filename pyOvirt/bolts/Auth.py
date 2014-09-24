# -*- coding: utf-8 -*-

from __future__ import print_function
from ovirtsdk.api import API as _API
import threading
import re
import logging
import copy
from time import (strftime, localtime, sleep)

from ovirtsdk.infrastructure.errors import (NoCertificatesError,
                                            ImmutableError,
                                            RequestError,
                                            ConnectionError,
                                            MissingParametersError)
 

log = logging.getLogger(__name__)


class _authPersist(threading.Thread):
    """ 
    arguments:
        ovauth: connected ovirtsdk api object

    This is meant to run in a thread 
    """

    def __init__(self, ovauth, interval=600, name=None):
        ''' ovirt api will be pinged every _interval_ seconds '''
        threading.Thread.__init__(self)
        self.daemon = True
        self._api = ovauth.connection
        self.interval = interval

    def run(self):
        while 1:
            self.api.vms.list(max=1)
            self._lastping = localtime()
            sleep(900)

    @property
    def api(self):
        return self._api

    @property
    def lastping(self):
        return strftime('%c', self._lastping)


class ovirtAuth(object):
    """ 
    arguments:
        url: ovirt manager url
        username
        password
        ca_file

        optional: 
            connection_name (symbolic name of connection)
    """

    _connections={}

    def __init__(self, 
                 username=None, password=None, 
                 url=None, ca_file=None, connection_name=None):

        self._connection_name=None
        self._illegals=[]
        self._id = id(self)

        for arg in [ username,  password, url ]:
            if not arg: 
                self._illegals.append(arg)

        if self._illegals:
            raise MissingParametersError('username, password, url, and ca_file ' 
                                         + 'location are required')

        # something to tell us something about the connection when interacting
        # with the class interactively
        
        if connection_name:
            self._connection_name = connection_name
        else:
            self._connection_name = re.sub(r'^https?://(.*)/?', r'\1', url)
        
        # if an API connection handle already exists for the requested host, use it.
        if self._connection_name in ovirtAuth._connections:
            self._connection = ovirtAuth._connections[self.connection_name]
            log.debug("connection exists.  reusing " + str(
                    ovirtAuth._connections[self.connection_name]))
        else:
            api_args = { 
                    'url': url,
                    'username': username,
                    'password': password,
                    'renew_session': True,
                    'session_timeout': 100000 }

            log.debug('connection initiated: {0}'.format(self.clean_args(api_args)))

            if ca_file:
                api_args.update({ 'ca_file': ca_file })
            else:
                api_args.update({ 'insecure': True })

            try:
                self._connection = _API(**api_args)

                ovirtAuth._connections[self._connection_name] =  self._connection
                self._ping = _authPersist(self, name=self._id)
                self._ping.start()

            except ( ConnectionError, NoCertificatesError, ImmutableError, 
                    RequestError ), e:
                
                print('wheeeee! {0}: '.format(e))

    @classmethod
    def clean_args(self, args ):
        if type(args) != type(dict()):
            return args

        dimlit = copy.deepcopy(args)
        obfuscatees = [ t for t in dimlit.keys() if re.search(r'pass', t, re.I) ]

        for el in obfuscatees:
            dimlit[el] = '***'

        return dimlit

    @classmethod
    def connections(self):
        conn = ovirtAuth._connections
        k = {}
        for el in conn:
            k.update({el: conn[el]})
        return k

    @classmethod
    def get_connection(self,name):
        if name in ovirtAuth._connections:
            return ovirtAuth._connections[name]
        else:
            return None

    @property
    def connection(self):
        return self._connection

    @property
    def connection_name(self):
        return self._connection_name


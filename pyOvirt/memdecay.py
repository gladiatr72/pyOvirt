# -*- coding: utf-8 -*-

from __future__ import print_function
import wrapt
import time
import copy
import sys

class memdecay(object):
    _cache = {}
    _command = ('refresh', 'stat')
    switches = {}

    def __init__(self, decay=None):
        self.decay = decay

    def _hash_gen(self, args, kwargs):
        kw_key = tuple([ 
            '{}:{}'.format(kw, kwargs[kw]) 
                for kw in copy.copy(kwargs)])
        return hash((kw_key, args))

    def _neuter_args(self, args):
        return tuple([ n for n in args if n not in self._command])


    @wrapt.decorator
    def __call__(self, wrapped, instance, args, kwargs):
        switches = [cmd for cmd in self._command if cmd in args]
        args = self._neuter_args(args)
        key = self._hash_gen(args,kwargs)
        cache = self._cache


        if key in self._cache:

            lifespan = time.time() - cache[key]['birth']
            if cache[key]['decay']:
                if lifespan >= cache[key]['decay']:
                    del cache[key]
                else:
                    if 'refresh' in switches:
                        del cache[key]
                    if 'stat' in switches:
                        log.info('lifespan: {0}/{1}'.format(int(lifespan),cache[key]['decay']), file=sys.stderr)
                        log.info('{0}\n{1}\n{2}'.format(
                            cache[key], '', ''), file=sys.stdout)

        if key not in cache:
            self._cache[key] = { 
                'function': wrapped(*args, **kwargs),
                'decay': self.decay,
                'birth': time.time() }

        return self._cache[key]['function']

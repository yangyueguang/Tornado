#! /usr/bin/env python
# coding: utf-8
# 把字典的调用转为点语法

class Dict(dict):
    def __init__(self, sdict={}):
        super(dict, self).__init__()
        if sdict is not None:
            for sk, sv in sdict.items():
                if isinstance(sv, dict):
                    self[sk] = Dict(sv)
                else:
                    self[sk] = sv

    """ A dict that allows for object-like property access syntax. """
    def __getattr__(self, name, default=None):
        try:
            return default if name not in self and default is not None else self[name]
        except KeyError:
            # raise AttributeError(name)
            return None

